gamemode survival @a
effect give @a minecraft:resistance infinite 255 true
effect give @a minecraft:saturation infinite 255 true
clear @a
place feature minecraft:spruce -4 -60 12
place feature minecraft:spruce 5 -60 10
place feature minecraft:spruce -9 -60 6
place feature minecraft:spruce 9 -60 4
place feature minecraft:spruce -6 -60 -8
place feature minecraft:spruce 7 -60 -9
place feature minecraft:spruce 2 -60 22
place feature minecraft:spruce -3 -60 25
setblock -3 -60 9 minecraft:oak_fence
setblock -3 -59 9 minecraft:lantern
setblock 3 -60 13 minecraft:oak_fence
setblock 3 -59 13 minecraft:lantern
setblock 2 -60 3 minecraft:campfire
setblock -2 -60 -4 minecraft:oak_fence
setblock -2 -59 -4 minecraft:soul_lantern
setblock 1 -60 18 minecraft:soul_lantern
tp @a 0 -60 0 facing 0 -58.5 16
summon korkumodu:albasti 0 -60 16
schedule function sahne:s2 100t
