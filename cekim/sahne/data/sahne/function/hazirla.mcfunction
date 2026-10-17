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
tp @a 0 -60 0 facing 0 -58.5 16
summon korkumodu:albasti 0 -60 16
schedule function sahne:s2 100t
