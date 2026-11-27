-- ZRY-FIRST-BREATH-001: five tracks, one NAFAS-*.mid each (file-referenced, as the smoke script
-- does), SINE Player on every track, 6/8 at quarter = 123 (dotted quarter 82), render settings
-- per the work order. Instrument states are spliced in afterwards from the saved ensemble /
-- Ratio projects (Scripts/splice_sine_states.py), so no instrument is loaded here.
local proj_dir = [[%ZIRYAB_STUDIO%/Projects/ZRY-FIRST-BREATH-001]]
local rpp = proj_dir .. [[/ZRY-FIRST-BREATH-001.rpp]]
local marker = proj_dir .. [[/Provenance/setup_done.txt]]
local render_end = 70.0  -- last note ends 65.69 s + 4 s tail, rounded up

local specs = {
  { "Strand_Nylon",  "NAFAS-gtr.mid" },
  { "Lucent_Flute",  "NAFAS-flt.mid" },
  { "Helix_Strings", "NAFAS-str.mid" },
  { "Ratio_Piano",   "NAFAS-pno.mid" },
  { "Crux_JBass",    "NAFAS-bas.mid" },
}

local log = {}
local function L(s) log[#log + 1] = s end

reaper.Undo_BeginBlock()
while reaper.CountTracks(0) > 0 do reaper.DeleteTrack(reaper.GetTrack(0, 0)) end
reaper.SetCurrentBPM(0, 123, false)
reaper.SetTempoTimeSigMarker(0, -1, 0, -1, -1, 123, 6, 8, false)
L("tempo_marker_count=" .. reaper.CountTempoTimeSigMarkers(0))
L("qn132_time=" .. string.format("%.4f", reaper.TimeMap_QNToTime(0, 132)))  -- last guitar onset, expect 64.39

for idx, s in ipairs(specs) do
  reaper.InsertTrackAtIndex(idx - 1, true)
  local tr = reaper.GetTrack(0, idx - 1)
  reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", s[1], true)
  local midi = proj_dir .. "/MIDI/" .. s[2]
  local src = reaper.PCM_Source_CreateFromFileEx(midi, true)
  if not src then L("FAIL source " .. midi) else
    local item = reaper.AddMediaItemToTrack(tr)
    local take = reaper.AddTakeToMediaItem(item)
    reaper.SetMediaItemTake_Source(take, src)
    local len, isqn = reaper.GetMediaSourceLength(src)
    local secs = isqn and reaper.TimeMap_QNToTime(0, len) or len
    reaper.SetMediaItemInfo_Value(item, "D_POSITION", 0)
    reaper.SetMediaItemInfo_Value(item, "D_LENGTH", secs)
    reaper.SetMediaItemInfo_Value(item, "B_LOOPSRC", 0)
    local fx = reaper.TrackFX_AddByName(tr, "VST3i: SINE Player (Orchestral Tools)", false, -1)
    L(string.format("%d\t%s\t%s\tsrclen=%.4f\tisqn=%s\tfx=%d", idx, s[1], s[2], secs, tostring(isqn), fx))
  end
end

reaper.GetSetProjectInfo(0, "RENDER_SETTINGS", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_BOUNDSFLAG", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_STARTPOS", 0, true)
reaper.GetSetProjectInfo(0, "RENDER_ENDPOS", render_end, true)
reaper.GetSetProjectInfo(0, "RENDER_SRATE", 44100, true)
reaper.GetSetProjectInfo(0, "RENDER_CHANNELS", 2, true)
reaper.GetSetProjectInfo(0, "RENDER_DITHER", 0, true)
reaper.GetSetProjectInfo_String(0, "RENDER_FILE", proj_dir .. "/Renders", true)
reaper.GetSetProjectInfo_String(0, "RENDER_PATTERN", "ZRY-FIRST-BREATH-001-mix", true)
reaper.GetSetProjectInfo_String(0, "RENDER_FORMAT", "evaw", true)

reaper.Main_SaveProjectEx(0, rpp, 8)
reaper.Undo_EndBlock("ZRY-FIRST-BREATH-001 setup", -1)

local f = io.open(marker, "w")
if f then f:write(table.concat(log, "\n") .. "\n"); f:close() end
reaper.Main_OnCommand(40004, 0) -- File: Quit REAPER
