import tkinter as tk
from model import RecommendationModel
from views import ColdStartApp

if __name__ == "__main__":
    # 1. 初始化資料與推薦模型（路徑對應到 data 資料夾中的 items.csv）
    recommender_model = RecommendationModel("data/items.csv")
    
    # 2. 建立主視窗與應用程式介面，並將 model 注入進去
    root = tk.Tk()
    app = ColdStartApp(root, recommender_model)
    
    # 3. 啟動事件循環
    root.mainloop()