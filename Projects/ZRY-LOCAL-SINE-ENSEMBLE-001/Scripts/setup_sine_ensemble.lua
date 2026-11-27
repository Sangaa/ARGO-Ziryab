-- ZRY-LOCAL-SINE-ENSEMBLE-001: one track per installed SINE instrument, each with SINE Player
-- and the Ratio test phrase fitted to the instrument's range. Instruments are loaded by hand
-- in SINE's UI (no scripting API); render_sine_ensemble.lua then renders each track solo.

local proj_dir = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-ENSEMBLE-001]]
local rpp = proj_dir .. [[/ZRY-LOCAL-SINE-ENSEMBLE-001.rpp]]
local marker = proj_dir .. [[/Provenance/setup_done.txt]]
local length = 8.0  -- 4 bars at 120 BPM

-- name, chord transpose (nil = no chords), melody transpose (nil = no melody), bass line?
local specs = {
  { "Helix_Strings",        0,   0,   false },
  { "Lucent_Flute",         nil, 0,   false },
  { "Manifold_Female",      12,  0,   false },
  { "Manifold_Male",        0,   -12, false },
  { "Strand_Nylon",         0,   -12, false },
  { "Strand_Steel",         0,   -12, false },
  { "Crux_JBass",           nil, nil, true  },
  { "Crux_MMBass",          nil, nil, true  },
  { "Crux_PBass",           nil, nil, true  },
  { "Crux_VBass",           nil, nil, true  },
  { "Clutch_Organ",         0,   0,   false },
  { "Crucible_ChurchOrgan", 0,   0,   false },
  { "Rotary_SoloTrumpet",   nil, -12, false },
  { "Rotary_TrumpetMute",   nil, -12, false },
  { "Rotary_TromboneSolo",  nil, -24, false },
  { "Rotary_BaritoneSax",   nil, -24, false },
  { "Rotary_SaxSection",    0,   -12, false },
  { "Rotary_BrassSection",  0,   -12, false },
}

local chords = { {48, 55, 64}, {45, 52, 60}, {41, 48, 57}, {43, 50, 59} } -- C Am F G
local melody = { 72, 74, 76, 79,  76, 74, 72, 71,  69, 72, 77, 76,  74, 71, 74, 72 }
local bass   = { 36, 33, 29, 31 }

reaper.Undo_BeginBlock()
while reaper.CountTracks(0) > 0 do reaper.DeleteTrack(reaper.GetTrack(0, 0)) end
reaper.SetCurrentBPM(0, 120, false)

local log = {}
for idx, s in ipairs(specs) do
  reaper.InsertTrackAtIndex(idx - 1, true)
  local tr = reaper.GetTrack(0, idx - 1)
  reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", s[1], true)
  local item = reaper.CreateNewMIDIItemInProj(tr, 0, length, false)
  local take = reaper.GetActiveTake(item)
  local function note(t, len, pitch, vel)
    local a = reaper.MIDI_GetPPQPosFromProjTime(take, t)
    local b = reaper.MIDI_GetPPQPosFromProjTime(take, t + len)
    reaper.MIDI_InsertNote(take, false, false, a, b, 0, pitch, vel, true)
  end
  if s[2] then
    for i, c in ipairs(chords) do
      for _, p in ipairs(c) do note((i - 1) * 2.0, 1.9, p + s[2], 70) end
    end
  end
  if s[3] then
    for i, p in ipairs(melody) do note((i - 1) * 0.5, 0.45, p + s[3], 88) end
  end
  if s[4] then
    for i, p in ipairs(bass) do
      note((i - 1) * 2.0, 0.9, p, 95)
      note((i - 1) * 2.0 + 1.0, 0.9, p + 7, 85)
    end
  end
  reaper.MIDI_Sort(take)
  local fx = reaper.TrackFX_AddByName(tr, "VST3i: SINE Player (Orchestral Tools)", false, -1)
  log[#log + 1] = idx .. "\t" .. s[1] .. "\tfx=" .. tostring(fx)
end

reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_STARTPOS", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_ENDPOS", length + 2.0, true)
reaper.GetSetProjectInfo(0, "RENDER_SRATE", 44100, true)
reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
reaper.GetSetProjectInfo(0, "RENDER_DITHER", 0, true)
reaper.GetSetProjectInfo_String(0, "RENDER_FILE", proj_dir .. "/Renders", true)
reaper.GetSetProjectInfo_String(0, "RENDER_FORMAT", "evaw", true)

reaper.Main_SaveProjectEx(0, rpp, 8)
reaper.Undo_EndBlock("ZIRYAB SINE ensemble setup", -1)

local f = io.open(marker, "w")
if f then f:write(table.concat(log, "\n") .. "\n"); f:close() end
