//! `bsa` — list and extract TES4-family BSA archives (Skyrim SE v105 / LZ4 frame,
//! Skyrim LE / FO3 / FNV v104 / zlib, Oblivion v103) using the `ba2` crate.
//!
//! Usage:
//!   bsa info    <archive.bsa>
//!   bsa list    <archive.bsa> [-f GLOB]... [--long]
//!   bsa extract <archive.bsa> <outdir> [-f GLOB]... [--dry-run] [-q]
//!
//! Paths are lowercased, use `/`, and are relative to the archive root
//! (e.g. `meshes/actors/character/behaviors/0_master.hkx`). GLOB is matched
//! case-insensitively against that full path; `*` does not cross `/`, `**` does.
//! A bare extension filter like `-f '*.hkx'` matches at any depth (`**/*.hkx`).

use anyhow::{bail, Context, Result};
use ba2::{
    prelude::*,
    tes4::{Archive, ArchiveOptions, File, FileCompressionOptions},
};
use globset::{GlobSet, GlobSetBuilder};
use std::{
    fs,
    io::{self, Write},
    path::{Component, Path, PathBuf},
    process::ExitCode,
};

struct Entry<'a> {
    path: String,
    file: &'a File<'a>,
}

fn key_name(name: &[u8], hash_hex: impl FnOnce() -> String) -> String {
    if name.is_empty() {
        hash_hex()
    } else {
        String::from_utf8_lossy(name)
            .replace('\\', "/")
            .to_lowercase()
    }
}

fn entries<'a>(archive: &'a Archive<'a>) -> Vec<Entry<'a>> {
    let mut out = Vec::new();
    for (dkey, dir) in archive {
        let dname = key_name(dkey.name(), || format!("#{:016x}", dkey.hash().numeric()));
        for (fkey, file) in dir {
            let fname = key_name(fkey.name(), || format!("#{:016x}", fkey.hash().numeric()));
            let path = if dname.is_empty() || dname == "." {
                fname
            } else {
                format!("{}/{}", dname.trim_matches('/'), fname)
            };
            out.push(Entry { path, file });
        }
    }
    out.sort_by(|a, b| a.path.cmp(&b.path));
    out
}

fn build_filter(globs: &[String]) -> Result<Option<GlobSet>> {
    if globs.is_empty() {
        return Ok(None);
    }
    let mut b = GlobSetBuilder::new();
    for g in globs {
        let g = g.replace('\\', "/").to_lowercase();
        let g = if g.contains('/') { g } else { format!("**/{g}") };
        b.add(
            globset::GlobBuilder::new(&g)
                .case_insensitive(true)
                .literal_separator(true)
                .build()
                .with_context(|| format!("bad glob {g:?}"))?,
        );
    }
    Ok(Some(b.build()?))
}

/// Reject absolute paths and `..` so a hostile archive cannot write outside `outdir`.
fn safe_join(outdir: &Path, rel: &str) -> Result<PathBuf> {
    let p = Path::new(rel);
    let mut out = outdir.to_path_buf();
    for c in p.components() {
        match c {
            Component::Normal(s) => out.push(s),
            Component::CurDir => {}
            _ => bail!("refusing unsafe path in archive: {rel:?}"),
        }
    }
    Ok(out)
}

fn open(path: &Path) -> Result<(Archive<'static>, ArchiveOptions)> {
    Archive::read(path).with_context(|| format!("reading {}", path.display()))
}

fn decompressed_bytes(file: &File, opts: &FileCompressionOptions) -> Result<Vec<u8>> {
    if file.is_compressed() {
        Ok(file.decompress(opts)?.as_bytes().to_vec())
    } else {
        Ok(file.as_bytes().to_vec())
    }
}

fn cmd_info(path: &Path) -> Result<()> {
    let (archive, meta) = open(path)?;
    let es = entries(&archive);
    let compressed = es.iter().filter(|e| e.file.is_compressed()).count();
    println!("archive:     {}", path.display());
    println!("version:     {}", meta.version() as u32);
    println!("flags:       {:?}", meta.flags());
    println!("types:       {:?}", meta.types());
    println!("directories: {}", archive.len());
    println!("files:       {} ({} compressed)", es.len(), compressed);
    Ok(())
}

fn cmd_list(path: &Path, filter: Option<&GlobSet>, long: bool) -> Result<()> {
    let (archive, _meta) = open(path)?;
    let stdout = io::stdout();
    let mut w = io::BufWriter::new(stdout.lock());
    for e in entries(&archive) {
        if filter.is_some_and(|f| !f.is_match(&e.path)) {
            continue;
        }
        let r = if long {
            let size = e.file.decompressed_len().unwrap_or(e.file.len());
            writeln!(
                w,
                "{:>10} {} {}",
                size,
                if e.file.is_compressed() { "c" } else { "-" },
                e.path
            )
        } else {
            writeln!(w, "{}", e.path)
        };
        if let Err(err) = r {
            if err.kind() == io::ErrorKind::BrokenPipe {
                return Ok(());
            }
            return Err(err.into());
        }
    }
    w.flush().ok();
    Ok(())
}

fn cmd_extract(
    path: &Path,
    outdir: &Path,
    filter: Option<&GlobSet>,
    dry_run: bool,
    quiet: bool,
) -> Result<()> {
    let (archive, meta) = open(path)?;
    let opts: FileCompressionOptions = (&meta).into();
    let (mut n, mut bytes, mut failed) = (0usize, 0u64, 0usize);
    for e in entries(&archive) {
        if filter.is_some_and(|f| !f.is_match(&e.path)) {
            continue;
        }
        let dst = safe_join(outdir, &e.path)?;
        if dry_run {
            println!("{}", dst.display());
            n += 1;
            continue;
        }
        match decompressed_bytes(e.file, &opts) {
            Ok(data) => {
                if let Some(parent) = dst.parent() {
                    fs::create_dir_all(parent)
                        .with_context(|| format!("mkdir {}", parent.display()))?;
                }
                fs::write(&dst, &data).with_context(|| format!("write {}", dst.display()))?;
                bytes += data.len() as u64;
                n += 1;
                if !quiet {
                    println!("{}", e.path);
                }
            }
            Err(err) => {
                failed += 1;
                eprintln!("error: {}: {err:#}", e.path);
            }
        }
    }
    eprintln!(
        "{} file(s){} {} bytes, {} failed",
        n,
        if dry_run { " would be extracted;" } else { " extracted;" },
        bytes,
        failed
    );
    if failed > 0 {
        bail!("{failed} file(s) failed to extract");
    }
    Ok(())
}

fn usage() -> &'static str {
    "usage:\n  bsa info    <archive.bsa>\n  bsa list    <archive.bsa> [-f GLOB]... [-l|--long]\n  bsa extract <archive.bsa> <outdir> [-f GLOB]... [-n|--dry-run] [-q|--quiet]\n\nGLOB matches the lowercase, /-separated path; '*.hkx' (no '/') matches at any depth."
}

fn run() -> Result<()> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut pos = Vec::new();
    let mut globs = Vec::new();
    let (mut long, mut dry, mut quiet) = (false, false, false);
    let mut it = args.into_iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "-f" | "--filter" => globs.push(it.next().context("-f needs a GLOB")?),
            "-l" | "--long" => long = true,
            "-n" | "--dry-run" => dry = true,
            "-q" | "--quiet" => quiet = true,
            "-h" | "--help" => {
                println!("{}", usage());
                return Ok(());
            }
            s if s.starts_with('-') && s.len() > 1 => bail!("unknown option {s}\n{}", usage()),
            _ => pos.push(a),
        }
    }
    let filter = build_filter(&globs)?;
    match pos.iter().map(String::as_str).collect::<Vec<_>>().as_slice() {
        ["info", a] => cmd_info(Path::new(a)),
        ["list" | "ls", a] => cmd_list(Path::new(a), filter.as_ref(), long),
        ["extract" | "x", a, o] => cmd_extract(Path::new(a), Path::new(o), filter.as_ref(), dry, quiet),
        _ => bail!("{}", usage()),
    }
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("bsa: {e:#}");
            ExitCode::FAILURE
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use ba2::tes4::{
        ArchiveFlags, ArchiveKey, ArchiveTypes, Directory, DirectoryKey, Version,
    };

    const XML: &[u8] = b"<?xml version=\"1.0\"?><hkpackfile>repeat repeat repeat repeat repeat</hkpackfile>\n";
    const HKX: &[u8] = &[0x57, 0xE0, 0xE0, 0x57, 0x10, 0xC0, 0xC0, 0x10, 0, 0, 0, 0, 8, 1, 0, 1];

    fn roundtrip(version: Version, compressed: bool) {
        let mut flags = ArchiveFlags::DIRECTORY_STRINGS | ArchiveFlags::FILE_STRINGS;
        if compressed {
            flags |= ArchiveFlags::COMPRESSED;
        }
        let copts = FileCompressionOptions::builder().version(version).build();
        let mk = |b: &'static [u8]| {
            let f = File::from_decompressed(b);
            if compressed { f.compress(&copts).unwrap() } else { f }
        };
        let d1: Directory = [
            (DirectoryKey::from(b"0_master.hkx"), mk(HKX)),
            (DirectoryKey::from(b"Project.XML"), mk(XML)),
        ]
        .into_iter()
        .collect();
        let d2: Directory = [(DirectoryKey::from(b"readme.txt"), mk(b"hello\n"))]
            .into_iter()
            .collect();
        let archive: Archive = [
            (ArchiveKey::from(b"meshes\\actors\\character\\behaviors"), d1),
            (ArchiveKey::from(b"meshes"), d2),
        ]
        .into_iter()
        .collect();
        let dir = std::env::temp_dir().join(format!(
            "bsa-test-{}-{}-{}",
            std::process::id(),
            version as u32,
            compressed
        ));
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(&dir).unwrap();
        let bsa = dir.join("t.bsa");
        let opts = ArchiveOptions::builder()
            .version(version)
            .flags(flags)
            .types(ArchiveTypes::MESHES | ArchiveTypes::MISC)
            .build();
        archive.write(&mut fs::File::create(&bsa).unwrap(), &opts).unwrap();

        let (back, meta) = open(&bsa).unwrap();
        assert_eq!(meta.version(), version);
        let paths: Vec<_> = entries(&back).into_iter().map(|e| e.path).collect();
        assert_eq!(
            paths,
            [
                "meshes/actors/character/behaviors/0_master.hkx",
                "meshes/actors/character/behaviors/project.xml",
                "meshes/readme.txt",
            ]
        );
        for e in entries(&back) {
            assert_eq!(e.file.is_compressed(), compressed, "{}", e.path);
            if compressed {
                // payload codec: LZ4 frame magic for SSE, zlib header for v104
                let b = e.file.as_bytes();
                match version {
                    Version::v105 => assert_eq!(&b[..4], &[0x04, 0x22, 0x4D, 0x18], "{}", e.path),
                    _ => assert_eq!(b[0], 0x78, "{}", e.path),
                }
            }
        }

        let out = dir.join("out");
        let f = build_filter(&["*.hkx".into(), "*.xml".into()]).unwrap();
        cmd_extract(&bsa, &out, f.as_ref(), false, true).unwrap();
        assert_eq!(
            fs::read(out.join("meshes/actors/character/behaviors/0_master.hkx")).unwrap(),
            HKX
        );
        assert_eq!(
            fs::read(out.join("meshes/actors/character/behaviors/project.xml")).unwrap(),
            XML
        );
        assert!(!out.join("meshes/readme.txt").exists());
        cmd_extract(&bsa, &out, None, false, true).unwrap();
        assert_eq!(fs::read(out.join("meshes/readme.txt")).unwrap(), b"hello\n");
        fs::remove_dir_all(&dir).unwrap();
    }

    #[test]
    fn sse_v105_lz4() {
        roundtrip(Version::v105, true);
    }
    #[test]
    fn sse_v105_uncompressed() {
        roundtrip(Version::v105, false);
    }
    #[test]
    fn le_v104_zlib() {
        roundtrip(Version::v104, true);
    }

    #[test]
    fn rejects_traversal() {
        assert!(safe_join(Path::new("/o"), "../etc/passwd").is_err());
        assert!(safe_join(Path::new("/o"), "/etc/passwd").is_err());
        assert!(safe_join(Path::new("/o"), "meshes/a.hkx").is_ok());
    }

    #[test]
    fn glob_semantics() {
        let f = build_filter(&["*.HKX".into()]).unwrap().unwrap();
        assert!(f.is_match("meshes/actors/character/behaviors/0_master.hkx"));
        let f = build_filter(&["meshes/actors/**/*.xml".into()]).unwrap().unwrap();
        assert!(f.is_match("meshes/actors/character/characters/defaultmale.xml"));
        assert!(!f.is_match("meshes/actors/character/characters/defaultmale.hkx"));
    }
}
