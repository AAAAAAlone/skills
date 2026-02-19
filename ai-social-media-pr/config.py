# AI Social Media PR - 网格与布局配置
# 截图含顶部登录栏与左侧导航栏，通过裁剪比例只保留 4×6 内容区

# 网格：4 行 × 6 列 = 24 个笔记
GRID_ROWS = 4
GRID_COLS = 6
GRID_CELLS = GRID_ROWS * GRID_COLS  # 24

# 整屏裁剪：排除顶部登录栏、左侧导航栏，只保留笔记内容区
# 比例相对于整图宽高（0~1）
# 典型 1920×1080：顶栏约 60~100px -> 0.06~0.10，左栏约 80~150px -> 0.04~0.08
CROP_TOP = 0.10   # 排除顶部登录栏
CROP_BOTTOM = 0.98
CROP_LEFT = 0.08  # 排除左侧导航栏
CROP_RIGHT = 0.98

# 每个格子内：封面占格子高度的比例（剩余为文案/标题区）
CELL_COVER_HEIGHT_RATIO = 0.72

REFERENCE_WIDTH = 1920
REFERENCE_HEIGHT = 1080
