local proj=0
local out=[[%ZIRYAB_STUDIO%/Projects/ZRY-I2-FUR-ELISE-001/Provenance/MIDI-TAIL-INSPECT.txt]]
local f=io.open(out,"w")
local function log(s) if f then f:write(s.."\n"); f:flush() end end
log("PROJECT="..reaper.GetProjectName(proj,""))
for i=0,reaper.CountTracks(proj)-1 do
  local tr=reaper.GetTrack(proj,i)
  local _,name=reaper.GetSetMediaTrackInfo_String(tr,"P_NAME","",false)
  if name=="Strand_Nylon" then
    local item=reaper.GetTrackMediaItem(tr,0)
    local take=item and reaper.GetActiveTake(item)
    if not take or not reaper.TakeIsMIDI(take) then log("ERROR=NO_MIDI_TAKE"); if f then f:close() end; return end
    local _,count=reaper.MIDI_CountEvts(take)
    log("NOTE_COUNT="..tostring(count))
    for n=0,count-1 do
      local ok,sel,mute,startppq,endppq,chan,pitch,vel=reaper.MIDI_GetNote(take,n)
      log(string.format("NOTE_%d ok=%s pitch=%d start=%d end=%d vel=%d",n+1,tostring(ok),pitch or -1,startppq or -1,endppq or -1,vel or -1))
    end
  end
end
if f then f:close() end
