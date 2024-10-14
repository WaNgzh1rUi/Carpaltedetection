import ruptures as rpt
import matplotlib.pyplot as plt
import numpy as np

# 生成示例数据
data = np.array(
        [2750, 3270, 27092, 4867, 4207, 271220, 1309, 2922, 17152, 4479, 29561, 22586, 462, 1777, 24737, 20985, 45366,
         38289,
         10532, 25305, 48545, 16545, 66822, 993020, 83510, 277000, 40337, 28709, 28313, 63622])


# pelt 方法，感觉不太准
algo = rpt.Pelt(model="l1", min_size=3)
algo.fit(data)
result = algo.predict(pen=100000)
print(result)
rpt.display(data, [], result)

algo = rpt.KernelCPD(kernel='linear', min_size=3)
algo.fit(data)
result = algo.predict(n_bkps=4)
print(result)
rpt.display(data, [], result)
# 内核更改检测
fig, ax = plt.subplots(3,1, figsize=(1280/96, 720/96), dpi=96)

for i, kernel in enumerate(['linear', 'rbf', 'cosine']):
    algo = rpt.KernelCPD(kernel=kernel, min_size=3)
    algo.fit(data)
    result = algo.predict(n_bkps=4)
    ax[i].plot(data)
    print(result)
    for bkp in result:
        ax[i].axvline(x=bkp, color='k', linestyle='--')
    ax[i].set_title(f"Kernel model with {kernel} kernel")
fig.tight_layout()

plt.show()



