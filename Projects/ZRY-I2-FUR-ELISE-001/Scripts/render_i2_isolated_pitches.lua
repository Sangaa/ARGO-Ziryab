local proj=0
local outdir=[[%ZIRYAB_STUDIO%/Projects/ZRY-I2-FUR-ELISE-001/Renders]]
local pattern=[[ZRY-I2-FUR-ELISE-001-NYLON-TAKE-07-ISOLATED-PITCHES]]
local out=outdir.."/"..pattern..".wav"
local logpath=[[%ZIRYAB_STUDIO%/Projects/ZRY-I2-FUR-ELISE-001/Provenance/TAKE-07-ISOLATED-PITCHES-render-log.txt]]
local function log(s)
  local f=io.open(logpath,"a")
  if f then f:write(os.date("!%Y-%m-%dT%H:%M:%SZ").." "..tostring(s).."\n"); f:close() end
end
local target=nil
for i=0,reaper.CountTracks(proj)-1 do
  local tr=reaper.GetTrack(proj,i)
  local _,name=reaper.GetSetMediaTrackInfo_String(tr,"P_NAME","",false)
  if name=="Strand_Nylon" then target=tr end
  reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",name~="Strand_Nylon" and 1 or 0)
  reaper.SetMediaTrackInfo_Value(tr,"I_SOLO",0)
end
if not target then log("ERROR=TRACK_MISSING"); return end
local item=reaper.GetTrackMediaItem(target,0)
local take=item and reaper.GetActiveTake(item)
if not take or not reaper.TakeIsMIDI(take) then log("ERROR=MIDI_TAKE_MISSING"); return end
reaper.MIDI_Sort(take)
local _,count=reaper.MIDI_CountEvts(take)
if count~=6 then log("ERROR=EXPECTED_SIX_NOTES got="..tostring(count)); return end
local pitches={}
for n=0,count-1 do
  local ok,sel,mute,startppq,endppq,chan,pitch,vel=reaper.MIDI_GetNote(take,n)
  if not ok or endppq<=startppq then log("ERROR=BAD_NOTE_"..tostring(n+1)); return end
  pitches[n+1]={pitch=pitch,vel=vel,chan=chan}
end
for n=0,count-1 do
  local x=pitches[n+1]
  local startppq=n*2880
  local endppq=startppq+240
  local ok=reaper.MIDI_SetNote(take,n,false,false,startppq,endppq,x.chan,x.pitch,x.vel,true)
  log(string.format("ISOLATED_NOTE_%d ok=%s pitch=%d start=%d end=%d vel=%d",n+1,tostring(ok),x.pitch,startppq,endppq,x.vel))
end
reaper.MIDI_Sort(take)
reaper.SetMediaItemInfo_Value(item,"D_LENGTH",18.0)
reaper.UpdateItemInProject(item)
reaper.MarkProjectDirty(proj)
reaper.UpdateArrange()
reaper.SetMediaTrackInfo_Value(reaper.GetMasterTrack(proj),"B_MUTE",0)
reaper.GetSetProjectInfo(proj,"RENDER_BOUNDSFLAG",0,true)
reaper.GetSetProjectInfo(proj,"RENDER_STARTPOS",0,true)
reaper.GetSetProjectInfo(proj,"RENDER_ENDPOS",17.5,true)
reaper.GetSetProjectInfo(proj,"RENDER_TAILFLAG",1,true)
reaper.GetSetProjectInfo(proj,"RENDER_TAILMS",750,true)
reaper.GetSetProjectInfo_String(proj,"RENDER_FILE",outdir,true)
reaper.GetSetProjectInfo_String(proj,"RENDER_PATTERN",pattern,true)
local flags=reaper.GetSetProjectInfo(proj,"RENDER_SETTINGS",0,false)
if math.floor(flags/1048576)%2==0 then flags=flags+1048576 end
reaper.GetSetProjectInfo(proj,"RENDER_SETTINGS",flags,true)
reaper.GetSetProjectInfo(proj,"RENDER_DELAY",2,true)
log("CONFIG output="..out.." bounds=0..17.5 seconds, tail=750ms, six pitches separated by 2.5 sec")
reaper.Main_OnCommand(40026,0)
reaper.Main_OnCommand(41824,0)
log("RENDER_ACTION_RETURNED")
local ok,summary=reaper.GetSetProjectInfo_String(proj,"RENDER_STATS","",false)
log("RENDER_STATS_OK="..tostring(ok).." SUMMARY="..tostring(summary))
reaper.Main_OnCommand(40026,0)
log("END")
