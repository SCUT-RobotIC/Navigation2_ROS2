ros2 run nav2_map_server map_saver_cli -f src/rc_nav_bringup/map/TestMap
#-f src/rc_nav_bringup/map/TestMap是保存的路径和文件名，可以根据需要修改，注意不要加后缀名，默认会生成pgm和yaml两种格式的地图文件
#保存到src/rc_nav_bringup/map/目录下名称自定义，生成两个文件：TestMap.yaml和TestMap.pgm 