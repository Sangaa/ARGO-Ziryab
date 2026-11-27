local out=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-E-ORIENTAL-BAND-001/Provenance/dsk_strings_scan.txt]]
while reaper.CountTracks(0)>0 do reaper.DeleteTrack(reaper.GetTrack(0,0)) end
reaper.InsertTrackAtIndex(0,true)
local tr=reaper.GetTrack(0,0)
local fx=reaper.TrackFX_AddByName(tr,"VSTi: DSK Strings (x86) (DSK Music)",false,-1)
if fx<0 then fx=reaper.TrackFX_AddByName(tr,"DSK Strings",false,-1) end
local f=io.open(out,"w")
f:write("fx="..tostring(fx).."\n")
if fx>=0 then
 local _,name=reaper.TrackFX_GetFXName(tr,fx,"")
 f:write("fxname="..name.."\n")
 local cur,cnt=reaper.TrackFX_GetPresetIndex(tr,fx)
 f:write("preset_index="..tostring(cur).." preset_count="..tostring(cnt).."\n")
 for i=0,math.max(0,cnt-1) do
  reaper.TrackFX_SetPresetByIndex(tr,fx,i)
  local ok,pn=reaper.TrackFX_GetPreset(tr,fx,"")
  f:write(string.format("preset %d %s\n",i,tostring(pn)))
 end
 local np=reaper.TrackFX_GetNumParams(tr,fx)
 f:write("params="..tostring(np).."\n")
 for p=0,math.min(np-1,80) do
   local _,pn=reaper.TrackFX_GetParamName(tr,fx,p,"")
   local val=reaper.TrackFX_GetParamNormalized(tr,fx,p)
   local _,fmt=reaper.TrackFX_GetFormattedParamValue(tr,fx,p,"")
   f:write(string.format("param %d name=%s norm=%.6f fmt=%s\n",p,tostring(pn),val,tostring(fmt)))
 end
end
f:close()
