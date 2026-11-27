local out=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-E-ORIENTAL-BAND-001/Provenance/dsk_world_stringz_scan.txt]]
while reaper.CountTracks(0)>0 do reaper.DeleteTrack(reaper.GetTrack(0,0)) end
reaper.InsertTrackAtIndex(0,true)
local tr=reaper.GetTrack(0,0)
reaper.GetSetMediaTrackInfo_String(tr,"P_NAME","DSK_World_Stringz_Audit",true)
local names={
  "VST3i: DSK World String (DSK Music)",
  "DSK World String",
  "VST3i: DSK World Stringz"
}
local fx=-1
for _,n in ipairs(names) do
  fx=reaper.TrackFX_AddByName(tr,n,false,-1)
  if fx>=0 then break end
end
local f=io.open(out,"w")
f:write("fx="..tostring(fx).."\n")
if fx>=0 then
  local _,fxname=reaper.TrackFX_GetFXName(tr,fx,"")
  f:write("fxname="..tostring(fxname).."\n")
  local cur,cnt=reaper.TrackFX_GetPresetIndex(tr,fx)
  f:write("preset_index="..tostring(cur).." preset_count="..tostring(cnt).."\n")
  for i=0,math.max(0,cnt-1) do
    reaper.TrackFX_SetPresetByIndex(tr,fx,i)
    local ok,pname=reaper.TrackFX_GetPreset(tr,fx,"")
    f:write(string.format("preset %d ok=%s name=%s\n",i,tostring(ok),tostring(pname)))
  end
  local np=reaper.TrackFX_GetNumParams(tr,fx)
  f:write("params="..tostring(np).."\n")
  for p=0,np-1 do
    local _,pn=reaper.TrackFX_GetParamName(tr,fx,p,"")
    if pn and pn~="" then
      local v=reaper.TrackFX_GetParamNormalized(tr,fx,p)
      f:write(string.format("param %d name=%s norm=%.6f\n",p,pn,v))
    end
  end
end
f:close()
