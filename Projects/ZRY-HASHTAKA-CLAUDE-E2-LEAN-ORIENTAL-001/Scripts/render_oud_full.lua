local events = dofile([[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Scripts/score_events.lua]])
local outdir=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001/Renders]]
local rpp=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001/OUD_FULL.rpp]]
while reaper.CountTracks(0)>0 do reaper.DeleteTrack(reaper.GetTrack(0,0)) end
reaper.InsertTrackAtIndex(0,true)
local tr=reaper.GetTrack(0,0)
reaper.GetSetMediaTrackInfo_String(tr,"P_NAME","Turkish_Oud",true)
local fx=reaper.TrackFX_AddByName(tr,"VST3i: DSK World String (DSK Music)",false,-1)
if fx<0 then fx=reaper.TrackFX_AddByName(tr,"DSK World String",false,-1) end
if fx<0 then reaper.ShowConsoleMsg("FAIL OUD FX\n"); return end
reaper.TrackFX_SetPresetByIndex(tr,fx,12)

local item=reaper.CreateNewMIDIItemInProj(tr,0,89,false)
local take=reaper.GetActiveTake(item)
local count=0
for _,e in ipairs(events["Strand_Nylon"]) do
  local p0=reaper.MIDI_GetPPQPosFromProjTime(take,e[1])
  local p1=reaper.MIDI_GetPPQPosFromProjTime(take,e[2])
  if p1<=p0 then p1=p0+1 end
  reaper.MIDI_InsertNote(take,false,false,p0,p1,0,e[3],math.min(115,e[4]+10),true)
  count=count+1
end
reaper.MIDI_Sort(take)
reaper.SetMediaTrackInfo_Value(tr,"D_VOL",0.90)
reaper.SetMediaTrackInfo_Value(tr,"D_PAN",-0.14)

reaper.GetSetProjectInfo(0,"RENDER_SETTINGS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_BOUNDSFLAG",0,true)
reaper.GetSetProjectInfo(0,"RENDER_STARTPOS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_ENDPOS",89,true)
reaper.GetSetProjectInfo(0,"RENDER_SRATE",44100,true)
reaper.GetSetProjectInfo(0,"RENDER_CHANNELS",2,true)
reaper.GetSetProjectInfo_String(0,"RENDER_FILE",outdir,true)
reaper.GetSetProjectInfo_String(0,"RENDER_PATTERN","E2-OUD-FULL",true)
reaper.GetSetProjectInfo_String(0,"RENDER_FORMAT","evaw",true)
reaper.Main_SaveProjectEx(0,rpp,8)
reaper.Main_OnCommand(41824,0)

local f=io.open([[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-E2-LEAN-ORIENTAL-001/Provenance/oud_done.txt]],"w")
if f then f:write("notes="..count.."\npreset=Program 13 Turkish Oud\n");f:close() end
