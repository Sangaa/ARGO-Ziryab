local srcproj=[[%ZIRYAB_STUDIO%/Projects/ZRY-LOCAL-SINE-ENSEMBLE-001/ZRY-LOCAL-SINE-ENSEMBLE-001.rpp]]
local events=dofile([[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-CLAUDE-D-REAL-BAND-001/Scripts/score_events.lua]])
local outdir=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-SOUND-MENU-001/Renders]]
local meta=[[%ZIRYAB_STUDIO%/Projects/ZRY-HASHTAKA-SOUND-MENU-001/Provenance/menu_render.txt]]

local startT=7.55
local endT=15.45
local phrase={}
for _,e in ipairs(events["Strand_Nylon"]) do
  if e[1]>=startT and e[1]<endT then
    table.insert(phrase,e)
  end
end

reaper.Main_openProject("noprompt:"..srcproj)

local names={"Strand_Steel","Strand_Nylon","Clutch","Crucible"}
local tracks={}

for i=0,reaper.CountTracks(0)-1 do
  local tr=reaper.GetTrack(0,i)
  local _,name=reaper.GetTrackName(tr)
  for _,want in ipairs(names) do
    if name==want and not tracks[want] then tracks[want]=tr end
  end
  reaper.SetMediaTrackInfo_Value(tr,"I_SOLO",0)
  reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",1)
end

local f=io.open(meta,"w")
for _,want in ipairs(names) do
  local tr=tracks[want]
  if not tr then
    f:write(want.."=MISSING\n")
  else
    -- clear old media items only in memory; project is not saved.
    for j=reaper.CountTrackMediaItems(tr)-1,0,-1 do
      local it=reaper.GetTrackMediaItem(tr,j)
      reaper.DeleteTrackMediaItem(tr,it)
    end

    local dur=(endT-startT)+1.0
    local item=reaper.CreateNewMIDIItemInProj(tr,0,dur,false)
    local take=reaper.GetActiveTake(item)
    local n=0
    for _,e in ipairs(phrase) do
      local a=e[1]-startT+0.25
      local b=e[2]-startT+0.25
      local p0=reaper.MIDI_GetPPQPosFromProjTime(take,a)
      local p1=reaper.MIDI_GetPPQPosFromProjTime(take,b)
      if p1<=p0 then p1=p0+1 end
      reaper.MIDI_InsertNote(take,false,false,p0,p1,0,e[3],e[4],true)
      n=n+1
    end
    reaper.MIDI_Sort(take)

    for i=0,reaper.CountTracks(0)-1 do
      local x=reaper.GetTrack(0,i)
      reaper.SetMediaTrackInfo_Value(x,"B_MUTE",1)
      reaper.SetMediaTrackInfo_Value(x,"I_SOLO",0)
    end
    reaper.SetMediaTrackInfo_Value(tr,"B_MUTE",0)
    reaper.SetMediaTrackInfo_Value(tr,"D_VOL",0.82)
    reaper.SetMediaTrackInfo_Value(tr,"D_PAN",0)

    reaper.GetSetProjectInfo(0,"RENDER_SETTINGS",0,true)
    reaper.GetSetProjectInfo(0,"RENDER_BOUNDSFLAG",0,true)
    reaper.GetSetProjectInfo(0,"RENDER_STARTPOS",0,true)
    reaper.GetSetProjectInfo(0,"RENDER_ENDPOS",dur,true)
    reaper.GetSetProjectInfo(0,"RENDER_SRATE",44100,true)
    reaper.GetSetProjectInfo(0,"RENDER_CHANNELS",2,true)
    reaper.GetSetProjectInfo_String(0,"RENDER_FILE",outdir,true)
    reaper.GetSetProjectInfo_String(0,"RENDER_PATTERN",want,true)
    reaper.GetSetProjectInfo_String(0,"RENDER_FORMAT","evaw",true)
    reaper.Main_OnCommand(41824,0)
    f:write(want.."=OK notes="..n.."\n")
  end
end
f:close()
