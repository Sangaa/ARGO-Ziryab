local proj=0
local logpath=[[%ZIRYAB_STUDIO%/Projects/ZRY-I2-FUR-ELISE-001/Provenance/SINE-UI-INSPECTION.txt]]
local f=io.open(logpath,"w")
local function log(s) if f then f:write(s.."\n"); f:flush() end end
for i=0,reaper.CountTracks(proj)-1 do
  local tr=reaper.GetTrack(proj,i)
  local _,name=reaper.GetSetMediaTrackInfo_String(tr,"P_NAME","",false)
  if name=="Strand_Nylon" then
    log("TRACK="..name.." FX_COUNT="..tostring(reaper.TrackFX_GetCount(tr)))
    log("FX_NAME="..select(2,reaper.TrackFX_GetFXName(tr,0,"")))
    reaper.TrackFX_Show(tr,0,3)
    log("SHOW_REQUESTED=true")
    break
  end
end
if f then f:close() end
