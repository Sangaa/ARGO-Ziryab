local proj = 0
local outdir = [[%ZIRYAB_STUDIO%/Projects/ZRY-I2-FUR-ELISE-001/Renders]]
local pattern = [[ZRY-I2-FUR-ELISE-001-NYLON-TAKE-05-GATE80]]
local out = outdir .. "/" .. pattern .. ".wav"
local logpath = [[%ZIRYAB_STUDIO%/Projects/ZRY-I2-FUR-ELISE-001/Provenance/TAKE-05-GATE80-render-log.txt]]
local function log(s)
  local f = io.open(logpath, "a")
  if f then f:write(os.date("!%Y-%m-%dT%H:%M:%SZ") .. " " .. tostring(s) .. "\n"); f:close() end
end

log("REASCRIPT_START")
local target = nil
for i = 0, reaper.CountTracks(proj) - 1 do
  local tr = reaper.GetTrack(proj, i)
  local _, name = reaper.GetSetMediaTrackInfo_String(tr, "P_NAME", "", false)
  if name == "Strand_Nylon" then target = tr end
  reaper.SetMediaTrackInfo_Value(tr, "B_MUTE", name ~= "Strand_Nylon" and 1 or 0)
  reaper.SetMediaTrackInfo_Value(tr, "I_SOLO", 0)
end
if not target then log("ERROR=STRAND_NYLON_TRACK_MISSING"); return end
local item = reaper.GetTrackMediaItem(target, 0)
if not item then log("ERROR=MIDI_ITEM_MISSING"); return end
local take = reaper.GetActiveTake(item)
if not take or not reaper.TakeIsMIDI(take) then log("ERROR=ACTIVE_TAKE_NOT_MIDI"); return end
local _, note_count = reaper.MIDI_CountEvts(take)
log("MIDI_NOTE_COUNT=" .. tostring(note_count))
for n = 0, note_count - 1 do
  local ok, selected, muted, startppq, endppq, chan, pitch, vel = reaper.MIDI_GetNote(take, n)
  if not ok then log("ERROR=NOTE_READ_" .. tostring(n)); return end
  local new_end = startppq + math.floor((endppq - startppq) * 0.8 + 0.5)
  local changed = reaper.MIDI_SetNote(take, n, selected, muted, startppq, new_end, chan, pitch, vel, true)
  log(string.format("GATE80_NOTE_%d ok=%s pitch=%d start=%d old_end=%d new_end=%d vel=%d", n+1, tostring(changed), pitch, startppq, endppq, new_end, vel))
end
reaper.MIDI_Sort(take)
reaper.MarkProjectDirty(proj)
reaper.UpdateArrange()

reaper.SetMediaTrackInfo_Value(reaper.GetMasterTrack(proj), "B_MUTE", 0)
reaper.GetSetProjectInfo(proj, "RENDER_BOUNDSFLAG", 0, true)
reaper.GetSetProjectInfo(proj, "RENDER_STARTPOS", 0, true)
reaper.GetSetProjectInfo(proj, "RENDER_ENDPOS", 2.5, true)
reaper.GetSetProjectInfo(proj, "RENDER_TAILFLAG", 1, true)
reaper.GetSetProjectInfo(proj, "RENDER_TAILMS", 750, true)
reaper.GetSetProjectInfo_String(proj, "RENDER_FILE", outdir, true)
reaper.GetSetProjectInfo_String(proj, "RENDER_PATTERN", pattern, true)
local flags = reaper.GetSetProjectInfo(proj, "RENDER_SETTINGS", 0, false)
if math.floor(flags / 1048576) % 2 == 0 then flags = flags + 1048576 end
reaper.GetSetProjectInfo(proj, "RENDER_SETTINGS", flags, true)
reaper.GetSetProjectInfo(proj, "RENDER_DELAY", 2, true)
log("RENDER_CONFIG flags=" .. tostring(flags) .. " start=0 end=2.5 tail_ms=750 delay=2 output=" .. out)
reaper.Main_OnCommand(40026, 0)
reaper.Main_OnCommand(41824, 0)
log("RENDER_ACTION_RETURNED")
local stats_ok, summary = reaper.GetSetProjectInfo_String(proj, "RENDER_STATS", "", false)
log("RENDER_STATS_OK=" .. tostring(stats_ok) .. " SUMMARY=" .. tostring(summary))
reaper.Main_OnCommand(40026, 0)
log("REASCRIPT_END")
