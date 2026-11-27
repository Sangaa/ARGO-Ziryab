local proj=0
local title=reaper.GetProjectName(proj,"")
local stem=string.gsub(title,"%.rpp$","")
local out=[[%ZIRYAB_STUDIO%/Projects/ZRY-I2-FUR-ELISE-001/Provenance/FX-STATE-]]..stem..[[.txt]]
local f=io.open(out,"w")
local function log(s) if f then f:write(s.."\n"); f:flush() end end
log("PROJECT="..title)
for ti=0,reaper.CountTracks(proj)-1 do
  local tr=reaper.GetTrack(proj,ti)
  local _,name=reaper.GetSetMediaTrackInfo_String(tr,"P_NAME","",false)
  log("TRACK="..name.." MUTE="..tostring(reaper.GetMediaTrackInfo_Value(tr,"B_MUTE")))
  local count=reaper.TrackFX_GetCount(tr)
  log("FX_COUNT="..tostring(count).." INSTRUMENT_FX_INDEX="..tostring(reaper.TrackFX_GetInstrument(tr)))
  for fx=0,count-1 do
    local ok,fxname=reaper.TrackFX_GetFXName(tr,fx,"")
    local enabled=reaper.TrackFX_GetEnabled(tr,fx)
    local offline=reaper.TrackFX_GetOffline(tr,fx)
    local guid=reaper.TrackFX_GetFXGUID(tr,fx)
    local io_ok,inpin,outpin=reaper.TrackFX_GetIOSize(tr,fx)
    log(string.format("FX_%d ok=%s name=%s enabled=%s offline=%s guid=%s io_ok=%s input_pins=%s output_pins=%s",fx,tostring(ok),fxname,tostring(enabled),tostring(offline),tostring(guid),tostring(io_ok),tostring(inpin),tostring(outpin)))
  end
end
if f then f:close() end
