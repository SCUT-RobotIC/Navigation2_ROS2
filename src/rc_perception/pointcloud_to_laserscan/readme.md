# 1. pointcloud_to_laserscan更改的地方
## 1. 增加命令行参数配置
- "target_frame" 处理后数据发布的参考坐标系
- "cloud_in_topic" 接收的3d点云数据话题
## 2. 算法参数配置
通过config下的parameters.yaml进行数据转化算法的配置
# 2. pointcloud_to_laserscan 算法原理
## 1. 坐标变换
如果点云的 frame_id 和目标坐标系（target_frame）不同，先通过 TF 将点云转换到目标坐标系。

## 2. 高度过滤
只保留在 min_height 到 max_height 范围内的点（通常只考虑地面附近的点）。

## 3. 极坐标投影
对每个点，计算其到原点的距离（range = hypot(x, y)）和角度（angle = atan2(y, x)）。

## 4. 角度和距离过滤
只保留在 angle_min 到 angle_max 范围内、距离在 range_min 到 range_max 范围内的点。

## 5. 生成 LaserScan
按照角度分辨率（angle_increment），将点投影到 2D 激光扫描的每个角度格子里，取距离最近的点作为该方向的激光测距值。

## 6. 发布 /scan 话题
最终生成的 sensor_msgs::msg::LaserScan 消息，发布到 /scan 话题。