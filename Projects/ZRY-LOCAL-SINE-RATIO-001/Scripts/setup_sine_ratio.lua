-- ZRY-LOCAL-SINE-RATIO-001: first real-instrument render.
-- Builds a track with SINE Player and a short piano phrase written as MIDI notes, sets render
-- settings and saves the project. The Ratio instrument is loaded by hand in SINE's own UI,
-- because SINE Player exposes no scripting API for choosing an instrument.

local proj_dir = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-RATIO-001]]
local rpp = proj_dir .. [[/ZRY-LOCAL-SINE-RATIO-001.rpp]]
local marker = proj_dir .. [[/Provenance/setup_done.txt]]
local length = 8.0  -- 4 bars at 120 BPM

reaper.Undo_BeginBlock()
while reaper.CountTracks(0) > 0 do reaper.DeleteTrack(reaper.GetTrack(0, 0)) end
reaper.SetCurrentBPM(0, 120, false)
reaper.InsertTrackAtIndex(0, true)
local tr = reaper.GetTrack(0, 0)
reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "SINE_RATIO_PIANO", true)

local item = reaper.CreateNewMIDIItemInProj(tr, 0, length, false)
local take = reaper.GetActiveTake(item)

local function note(start_s, len_s, pitch, vel)
  local s = reaper.MIDI_GetPPQPosFromProjTime(take, start_s)
  local e = reaper.MIDI_GetPPQPosFromProjTime(take, start_s + len_s)
  reaper.MIDI_InsertNote(take, false, false, s, e, 0, pitch, vel, true)
end

-- Left hand: C - Am - F - G, one chord per bar (2 s).
local chords = { {48, 55, 64}, {45, 52, 60}, {41, 48, 57}, {43, 50, 59} }
for i, c in ipairs(chords) do
  for _, p in ipairs(c) do note((i - 1) * 2.0, 1.9, p, 70) end
end
-- Right hand: a simple quarter-note line (0.5 s each).
local melody = { 72, 74, 76, 79,  76, 74, 72, 71,  69, 72, 77, 76,  74, 71, 74, 72 }
for i, p in ipairs(melody) do note((i - 1) * 0.5, 0.45, p, 88) end
reaper.MIDI_Sort(take)

local fx = reaper.TrackFX_AddByName(tr, "VST3i: SINE Player (Orchestral Tools)", false, -1)
if fx < 0 then fx = reaper.TrackFX_AddByName(tr, "SINE Player (Orchestral Tools)", false, -1) end

reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_STARTPOS", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_ENDPOS", length + 2.0, true) -- 2 s release tail
reaper.GetSetProjectInfo(0, "RENDER_SRATE", 44100, true)
reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
reaper.GetSetProjectInfo(0, "RENDER_DITHER", 0, true)
reaper.GetSetProjectInfo_String(0, "RENDER_FILE", proj_dir .. "/Renders", true)
reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", "ZRY-LOCAL-SINE-RATIO-001", true)
reaper.GetSetProjectInfo_String(0, "RENDER_FORMAT", "evaw", true)

reaper.Main_SaveProjectEx(0, rpp, 8)
reaper.Undo_EndBlock("ZIRYAB SINE Ratio setup", -1)
if fx >= 0 then reaper.TrackFX_Show(tr, fx, 3) end

local f = io.open(marker, "w")
if f then f:write("fx_index=" .. tostring(fx) .. "\n"); f:close() end
