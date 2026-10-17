tag @s add basladi
gamemode survival @s
effect give @s minecraft:resistance infinite 3 true
effect give @s minecraft:saturation infinite 255 true
clear @s
item replace entity @s hotbar.0 with minecraft:torch 32
item replace entity @s hotbar.1 with minecraft:iron_sword
item replace entity @s hotbar.3 with minecraft:bread 12
tp @s 0 -60 0 0 0
schedule function sahne:a_cikis 150t
schedule function sahne:b_arkada 310t
schedule function sahne:c_dibinde 470t
schedule function sahne:d_ciglik 482t
schedule function sahne:e_nazar 520t
