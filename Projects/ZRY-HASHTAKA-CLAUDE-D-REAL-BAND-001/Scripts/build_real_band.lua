local proj = [[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001.rpp]]
local renderDir = [[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Renders]]
local marker = [[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Provenance/reaper_done.txt]]
local tabla = [[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-LAB-001/Renders/HASHTAKA-B_REAL_SAMPLES-TABLA-STEM.wav]]

local map = {
  Strand_Nylon = {file=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/MIDI/HASHTAKA-gtr.mid]], vol=0.50, pan=-0.26},
  Lucent_Flute = {file=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/MIDI/HASHTAKA-flt.mid]], vol=0.86, pan=0.22},
  Helix_Strings = {file=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/MIDI/HASHTAKA-str.mid]], vol=0.74, pan=0.34},
  Ratio_Piano = {file=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/MIDI/HASHTAKA-pno.mid]], vol=0.50, pan=-0.38},
  Crux_JBass = {file=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/MIDI/HASHTAKA-bas.mid]], vol=0.86, pan=0.00},
}

local function clear_items(tr)
  for i=reaper.CountTrackMediaItems(tr)-1,0,-1 do
    local it=reaper.GetTrackMediaItem(tr,i)
    reaper.DeleteTrackMediaItem(tr,it)
  end
end

local function add_source(tr, path, length)
  local src = reaper.PCM_Source_CreateFromFileEx(path, true)
  if not src then return false end
  local item = reaper.AddMediaItemToTrack(tr)
  local take = reaper.AddTakeToMediaItem(item)
  reaper.SetMediaItemTake_Source(take, src)
  reaper.SetMediaItemInfo_Value(item, "D_POSITION", 0.0)
  reaper.SetMediaItemInfo_Value(item, "D_LENGTH", length)
  return true
end

reaper.Main_openProject("noprompt:" .. proj)
reaper.Undo_BeginBlock()
reaper.SetCurrentBPM(0,112.0,true)

local found={}
for i=0,reaper.CountTracks(0)-1 do
  local tr=reaper.GetTrack(0,i)
  local ok,name=reaper.GetTrackName(tr)
  if map[name] then
    clear_items(tr)
    if not add_source(tr,map[name].file,89.0) then
      reaper.ShowConsoleMsg("FAIL MIDI "..name.."\n")
      return
    end
    reaper.SetMediaTrackInfo_Value(tr,"D_VOL",map[name].vol * 0.72)
    reaper.SetMediaTrackInfo_Value(tr,"D_PAN",map[name].pan)
    reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",0)
    found[name]=true
  end
end

for name,_ in pairs(map) do
  if not found[name] then
    reaper.ShowConsoleMsg("MISSING TRACK "..name.."\n")
    return
  end
end

reaper.InsertTrackAtIndex(reaper.CountTracks(0),true)
local tt=reaper.GetTrack(0,reaper.CountTracks(0)-1)
reaper.GetSetMediaTrackInfo_String(tt,"P_NAME","Tabla_Real_B",true)
if not add_source(tt,tabla,89.0) then
  reaper.ShowConsoleMsg("FAIL TABLA\n")
  return
end
reaper.SetMediaTrackInfo_Value(tt,"D_VOL",0.34)
reaper.SetMediaTrackInfo_Value(tt,"D_PAN",0.0)

reaper.GetSetProjectInfo(0,"RENDER_SETTINGS",0,true)
reaper.GetSetProjectInfo(0,"RENDER_BOUNDSFLAG",0,true)
reaper.GetSetProjectInfo(0,"RENDER_STARTPOS",0.0,true)
reaper.GetSetProjectInfo(0,"RENDER_ENDPOS",89.0,true)
reaper.GetSetProjectInfo(0,"RENDER_SRATE",44100,true)
reaper.GetSetProjectInfo(0,"RENDER_CHANNELS",2,true)
reaper.GetSetProjectInfo_String(0,"RENDER_FILE",renderDir,true)
reaper.GetSetProjectInfo_String(0,"RENDER_PATTERN","HASHTAKA-D_REAL_BAND_RAW",true)
reaper.GetSetProjectInfo_String(0,"RENDER_FORMAT","evaw",true)

reaper.Main_SaveProjectEx(0,proj,8)
reaper.Undo_EndBlock("HASHTAKA real-band same-score build",-1)
reaper.Main_OnCommand(41824,0)

local f=io.open(marker,"w")
if f then
  f:write("same_score=true\n")
  f:write("tabla=B_REAL_SAMPLES\n")
  f:write("tempo=112\n")
  f:close()
end
