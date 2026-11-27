-- Listening feedback (2026-10-08): the Crux basses and the two organs sounded weak on the
-- laptop speakers. Measured cause: 52-78 % of the bass energy is below 150 Hz. This renders
-- "-oct-up" variants (basses +12 semitones; organ chord notes below 66 +12, melody unchanged),
-- then restores the original notes and leaves the saved project exactly as it was.
local proj_dir = [[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-ENSEMBLE-001]]
local marker = proj_dir .. [[/Provenance/octave_up_done.txt]]
local targets = {
  Crux_JBass = "all", Crux_MMBass = "all", Crux_PBass = "all", Crux_VBass = "all",
  Clutch_Organ = "chords", Crucible_ChurchOrgan = "chords",
}

-- Raise notes and remember every original pitch, so restore() puts back exactly what was there.
local saved = {}
local function raise(take, mode)
  local orig = {}
  local _, n = reaper.MIDI_CountEvts(take)
  for k = 0, n - 1 do
    local _, sel, mut, s, e, chan, pitch, vel = reaper.MIDI_GetNote(take, k)
    orig[#orig + 1] = { s, e, chan, pitch, vel, sel, mut }
    if mode == "all" or pitch < 66 then
      reaper.MIDI_SetNote(take, k, sel, mut, s, e, chan, pitch + 12, vel, true)
    end
  end
  reaper.MIDI_Sort(take)
  saved[take] = orig
end
local function restore(take)
  local _, n = reaper.MIDI_CountEvts(take)
  for k = n - 1, 0, -1 do reaper.MIDI_DeleteNote(take, k) end
  for _, o in ipairs(saved[take]) do
    reaper.MIDI_InsertNote(take, o[6], o[7], o[1], o[2], o[3], o[4], o[5], true)
  end
  reaper.MIDI_Sort(take)
end

local function each_target(fn)
  for i = 0, reaper.CountTracks(0) - 1 do
    local tr = reaper.GetTrack(0, i)
    local _, name = reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "", false)
    if targets[name] then fn(tr, name, reaper.GetActiveTake(reaper.GetTrackMediaItem(tr, 0))) end
  end
end

local n = reaper.CountTracks(0)
local log = {}
each_target(function(tr, name, take) raise(take, targets[name]) end)
each_target(function(tr, name, take)
  for j = 0, n - 1 do
    local o = reaper.GetTrack(0, j)
    reaper.SetMediaTrackInfo_Value(o, "I_SOLO", (o == tr) and 2 or 0)
  end
  reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", "ZRY-SINE-" .. name .. "-oct-up", true)
  reaper.Main_OnCommand(41824, 0)
  log[#log + 1] = name
end)
for j = 0, n - 1 do reaper.SetMediaTrackInfo_Value(reaper.GetTrack(0, j), "I_SOLO", 0) end
each_target(function(tr, name, take) restore(take) end)
reaper.Main_OnCommand(40026, 0) -- save, back in the original state

local f = io.open(marker, "w")
if f then f:write(table.concat(log, "\n") .. "\n"); f:close() end
