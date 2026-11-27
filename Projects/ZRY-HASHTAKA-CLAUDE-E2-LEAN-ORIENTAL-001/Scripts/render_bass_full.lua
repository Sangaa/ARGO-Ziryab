local srcproj=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001.rpp]]
local outdir=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001/Renders]]
local marker=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001/Provenance/bass_done.txt]]
reaper.Main_openProject("noprompt:"..srcproj)
local bass=nil
for i=0,reaper.CountTracks(0)-1 do
  local tr=reaper.GetTrack(0,i)
  local _,name=reaper.GetTrackName(tr)
  reaper.SetMediaTrackInfo_Value(tr,"I_SOLO",0)
  reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",1)
  if name=="Crux_JBass" then bass=tr end
end
if not bass then reaper.ShowConsoleMsg("NO BASS\n"); return end
reaper.SetMediaTrackInfo_Value(bass,"B_MUTE",0)
reaper.SetMediaTrackInfo_Value(bass,"D_VOL",0.90)
reaper.SetMediaTrackInfo_Value(bass,"D_PAN",0.0)

reaper.GetSetProjectInfo(0,"RENDER_SETTINGS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_BOUNDSFLAG",0,true)
reaper.GetSetProjectInfo(0,"RENDER_STARTPOS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_ENDPOS",89,true)
reaper.GetSetProjectInfo(0,"RENDER_SRATE",44100,true)
reaper.GetSetProjectInfo(0,"RENDER_CHANNELS",2,true)
reaper.GetSetProjectInfo_String(0,"RENDER_FILE",outdir,true)
reaper.GetSetProjectInfo_String(0,"RENDER_PATTERN","E2-BASS-FULL",true)
reaper.GetSetProjectInfo_String(0,"RENDER_FORMAT","evaw",true)
reaper.Main_OnCommand(41824,0)
local f=io.open(marker,"w")
if f then f:write("track=Crux_JBass\n");f:close() end
