COMPS={
 'L_root_modifiers':[('0_master.xml','RootModifierList',[],False)],
 'L_mt_default':[('mt_behavior.xml','MT_Default_Behavior',['IdleBFR','SprintBFR','SneakIdleTurnState','MT_Sneak_Locomotion_State'],True,['MT_Default_Behavior'])],
 'L_sprint':[('sprintbehavior.xml',None,[],False)],
 'L_jump':[('0_master.xml',s,[],True,['RootBehaviorGraph']) for s in ['JumpStanding','JumpFastDirectional','JumpFallState','JumpLandState','JumpFallDirectionalBlend','JumpLandDirectionalBlend']],
 'W_1hm_standing':[('1hm_behavior.xml','1HM_Standing_Locomotion_Behavior',['Weapon_Locomotion_BFR'],True,['1HM_Standing_Locomotion_Behavior'])],
 'W_1hm_locomotion':[('1hm_locomotion.xml',None,['sprintBFR'],False)],
 'W_1hm_ready_mods':[('1hm_behavior.xml','1HM_Ready_State_MG',['1HM_Readied_BehaviorGraph'],False)],
 'A_attack_right':[('1hm_behavior.xml','AttackRight_State',['AttackRight_H2H','AttackRight_2HM_Sword','AttackRight_2HW','1HM_AttackRightRoot_Player_OLD','1HM_AttackRight_SneakState','AttackRight_StaffLeftBlend'],True,['1HM_AttackBehavior','1HM_Behavior'])],
}
OUTC={}
for k,spec in COMPS.items():
    RES={'vars':{},'events':{},'clips':set(),'brg':set(),'charprops':set()}
    for sp in spec: run(*sp)
    OUTC[k]={kk:RES[kk] for kk in RES}
print(json.dumps(OUTC,default=ser))
