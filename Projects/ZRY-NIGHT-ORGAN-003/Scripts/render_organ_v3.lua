local srcproj=[[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-ENSEMBLE-001/ZRY-LOCAL-SINE-ENSEMBLE-001.rpp]]
local events=dofile([[%ZIRYAB_STUDIO%/Projects/ZRY-NIGHT-ORGAN-003/Scripts/score_events.lua]])
local outdir=[[%ZIRYAB_STUDIO%/Projects/ZRY-NIGHT-ORGAN-003/Renders]]
local marker=[[%ZIRYAB_STUDIO%/Projects/ZRY-NIGHT-ORGAN-003/Provenance/organ_done.txt]]
reaper.Main_openProject("noprompt:"..srcproj)
reaper.SetCurrentBPM(0,92.0,true)

local target=nil
for i=0,reaper.CountTracks(0)-1 do
  local tr=reaper.GetTrack(0,i)
  local _,name=reaper.GetTrackName(tr)
  reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",1)
  reaper.SetMediaTrackInfo_Value(tr,"I_SOLO",0)
  if name=="Clutch_Organ" then target=tr end
end
if not target then reaper.ShowConsoleMsg("NO ORGAN\n"); return end
for j=reaper.CountTrackMediaItems(target)-1,0,-1 do
  reaper.DeleteTrackMediaItem(target,reaper.GetTrackMediaItem(target,j))
end
local item=reaper.CreateNewMIDIItemInProj(target,0,38.0,false)
local take=reaper.GetActiveTake(item)
local n=0
for _,e in ipairs(events.organ) do
  local p0=reaper.MIDI_GetPPQPosFromProjTime(take,e[1])
  local p1=reaper.MIDI_GetPPQPosFromProjTime(take,e[2])
  if p1<=p0 then p1=p0+1 end
  if reaper.MIDI_InsertNote(take,false,false,p0,p1,0,e[3],e[4],true) then n=n+1 end
end
reaper.MIDI_Sort(take)
reaper.SetMediaTrackInfo_Value(target,"B_MUTE",0)
reaper.SetMediaTrackInfo_Value(target,"D_VOL",0.72)
reaper.SetMediaTrackInfo_Value(target,"D_PAN",-0.08)

reaper.GetSetProjectInfo(0,"RENDER_SETTINGS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_BOUNDSFLAG",0,true)
reaper.GetSetProjectInfo(0,"RENDER_STARTPOS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_ENDPOS",38.0,true)
reaper.GetSetProjectInfo(0,"RENDER_SRATE",44100,true)
reaper.GetSetProjectInfo(0,"RENDER_CHANNELS",2,true)
reaper.GetSetProjectInfo_String(0,"RENDER_FILE",outdir,true)
reaper.GetSetProjectInfo_String(0,"RENDER_PATTERN","ORGAN_CONTINUOUS_STEM",true)
reaper.GetSetProjectInfo_String(0,"RENDER_FORMAT","evaw",true)
reaper.Main_OnCommand(41824,0)

local f=io.open(marker,"w")
if f then f:write("organ_notes="..n.."\ncontinuous=true\n"); f:close() end
