local srcproj=[[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-ENSEMBLE-001/ZRY-LOCAL-SINE-ENSEMBLE-001.rpp]]
local events=dofile([[%ZIRYAB_STUDIO%/Projects/ZRY-NYLON-TABLA-001/Scripts/score_events.lua]])
local outdir=[[%ZIRYAB_STUDIO%/Projects/ZRY-NYLON-TABLA-001/Renders]]
local marker=[[%ZIRYAB_STUDIO%/Projects/ZRY-NYLON-TABLA-001/Provenance/sine_stems_done.txt]]

reaper.Main_openProject("noprompt:"..srcproj)
reaper.SetCurrentBPM(0,96.0,true)

local wanted={Strand_Nylon="guitar",Crux_JBass="bass"}
local tracks={}
for i=0,reaper.CountTracks(0)-1 do
  local tr=reaper.GetTrack(0,i)
  local _,name=reaper.GetTrackName(tr)
  if wanted[name] then tracks[name]=tr end
  reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",1)
  reaper.SetMediaTrackInfo_Value(tr,"I_SOLO",0)
end

local function clear_items(tr)
  for j=reaper.CountTrackMediaItems(tr)-1,0,-1 do
    local it=reaper.GetTrackMediaItem(tr,j)
    reaper.DeleteTrackMediaItem(tr,it)
  end
end

local function insert_events(tr, evs)
  clear_items(tr)
  local item=reaper.CreateNewMIDIItemInProj(tr,0,44.0,false)
  local take=reaper.GetActiveTake(item)
  local n=0
  for _,e in ipairs(evs) do
    local p0=reaper.MIDI_GetPPQPosFromProjTime(take,e[1])
    local p1=reaper.MIDI_GetPPQPosFromProjTime(take,e[2])
    if p1<=p0 then p1=p0+1 end
    if reaper.MIDI_InsertNote(take,false,false,p0,p1,0,e[3],e[4],true) then n=n+1 end
  end
  reaper.MIDI_Sort(take)
  return n
end

local counts={}
counts.guitar=insert_events(tracks["Strand_Nylon"],events.guitar)
counts.bass=insert_events(tracks["Crux_JBass"],events.bass)

local function render_one(track, pattern, vol, pan)
  for i=0,reaper.CountTracks(0)-1 do
    local tr=reaper.GetTrack(0,i)
    reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",1)
    reaper.SetMediaTrackInfo_Value(tr,"I_SOLO",0)
  end
  reaper.SetMediaTrackInfo_Value(track,"B_MUTE",0)
  reaper.SetMediaTrackInfo_Value(track,"D_VOL",vol)
  reaper.SetMediaTrackInfo_Value(track,"D_PAN",pan)
  reaper.GetSetProjectInfo(0,"RENDER_SETTINGS",0,true)
  reaper.GetSetProjectInfo(0,"RENDER_BOUNDSFLAG",0,true)
  reaper.GetSetProjectInfo(0,"RENDER_STARTPOS",0,true)
  reaper.GetSetProjectInfo(0,"RENDER_ENDPOS",44.0,true)
  reaper.GetSetProjectInfo(0,"RENDER_SRATE",44100,true)
  reaper.GetSetProjectInfo(0,"RENDER_CHANNELS",2,true)
  reaper.GetSetProjectInfo_String(0,"RENDER_FILE",outdir,true)
  reaper.GetSetProjectInfo_String(0,"RENDER_PATTERN",pattern,true)
  reaper.GetSetProjectInfo_String(0,"RENDER_FORMAT","evaw",true)
  reaper.Main_OnCommand(41824,0)
end

render_one(tracks["Strand_Nylon"],"NYLON_GUITAR_STEM",0.92,-0.08)
render_one(tracks["Crux_JBass"],"BASS_STEM",0.95,0.0)

local f=io.open(marker,"w")
if f then
 f:write("guitar_notes="..counts.guitar.."\n")
 f:write("bass_notes="..counts.bass.."\n")
 f:close()
end
