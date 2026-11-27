local events = dofile([[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Scripts/score_events.lua]])
local marker = [[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Provenance/reaper_done_v2.txt]]
local renderDir = [[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Renders]]

local function clear_items(tr)
  for i=reaper.CountTrackMediaItems(tr)-1,0,-1 do
    local it=reaper.GetTrackMediaItem(tr,i)
    reaper.DeleteTrackMediaItem(tr,it)
  end
end

reaper.Undo_BeginBlock()
local counts={}
for i=0,reaper.CountTracks(0)-1 do
  local tr=reaper.GetTrack(0,i)
  local _,name=reaper.GetTrackName(tr)
  if events[name] then
    clear_items(tr)
    local item=reaper.CreateNewMIDIItemInProj(tr,0.0,89.0,false)
    local take=reaper.GetActiveTake(item)
    local n=0
    for _,e in ipairs(events[name]) do
      local p0=reaper.MIDI_GetPPQPosFromProjTime(take,e[1])
      local p1=reaper.MIDI_GetPPQPosFromProjTime(take,e[2])
      if p1 <= p0 then p1=p0+1 end
      if reaper.MIDI_InsertNote(take,false,false,p0,p1,0,e[3],e[4],true) then n=n+1 end
    end
    reaper.MIDI_Sort(take)
    counts[name]=n
  end
end

reaper.GetSetProjectInfo(0,"RENDER_SETTINGS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_BOUNDSFLAG",0,true)
reaper.GetSetProjectInfo(0,"RENDER_STARTPOS",0.0,true)
reaper.GetSetProjectInfo(0,"RENDER_ENDPOS",89.0,true)
reaper.GetSetProjectInfo(0,"RENDER_SRATE",44100,true)
reaper.GetSetProjectInfo(0,"RENDER_CHANNELS",2,true)
reaper.GetSetProjectInfo_String(0,"RENDER_FILE",renderDir,true)
reaper.GetSetProjectInfo_String(0,"RENDER_PATTERN","HASHTAKA-D_REAL_BAND_RAW-v2",true)
reaper.GetSetProjectInfo_String(0,"RENDER_FORMAT","evaw",true)
reaper.Main_SaveProject(0,false)
reaper.Undo_EndBlock("Insert actual Hashtaka MIDI notes",-1)

reaper.Main_OnCommand(41824,0)

local f=io.open(marker,"w")
if f then
  for k,v in pairs(counts) do f:write(k.."="..v.."\n") end
  f:close()
end
