local midi = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SMOKE-002-AUTO/MIDI/ZRY-LOCAL-SMOKE-002-AUTO.mid]]
local rpp = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SMOKE-002-AUTO/ZRY-LOCAL-SMOKE-002-AUTO.rpp]]
local renderDir = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SMOKE-002-AUTO/Renders]]
local marker = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SMOKE-002-AUTO/Provenance/reaper_done.txt]]

reaper.Undo_BeginBlock()
while reaper.CountTracks(0) > 0 do reaper.DeleteTrack(reaper.GetTrack(0,0)) end
reaper.InsertTrackAtIndex(0, true)
local tr = reaper.GetTrack(0,0)
reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "ZIRYAB_SMOKE_REASYNTH", true)

local src = reaper.PCM_Source_CreateFromFileEx(midi, true)
if not src then reaper.ShowConsoleMsg("FAIL: MIDI source create\n"); return end
local item = reaper.AddMediaItemToTrack(tr)
local take = reaper.AddTakeToMediaItem(item)
reaper.SetMediaItemTake_Source(take, src)
reaper.SetMediaItemInfo_Value(item, "D_POSITION", 0)
reaper.SetMediaItemInfo_Value(item, "D_LENGTH", 6.0)

local fx = reaper.TrackFX_AddByName(tr, "ReaSynth (Cockos)", false, -1)
if fx < 0 then fx = reaper.TrackFX_AddByName(tr, "VSTi: ReaSynth (Cockos)", false, -1) end
if fx < 0 then reaper.ShowConsoleMsg("FAIL: ReaSynth not found\n"); return end

reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_STARTPOS", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_ENDPOS", 6.0, true)
reaper.GetSetProjectInfo(0, "RENDER_SRATE", 44100, true)
reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
reaper.GetSetProjectInfo_String(0, "RENDER_FILE", renderDir, true)
reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", "ZRY-LOCAL-SMOKE-002-AUTO", true)
reaper.GetSetProjectInfo_String(0, "RENDER_FORMAT", "evaw", true)

reaper.Main_SaveProjectEx(0, rpp, 8)
reaper.Undo_EndBlock("ZIRYAB automatic smoke setup", -1)
reaper.Main_OnCommand(41824, 0)

local f = io.open(marker, "w")
if f then
  f:write("fx_index=" .. tostring(fx) .. "\n")
  f:write("midi=" .. midi .. "\n")
  f:close()
end
