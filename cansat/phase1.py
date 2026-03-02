import time
import timeout_decorator

from BNO055 import BNO055
from MS5607 import MS5607


@timeout_decorator.timeout(3600)
def phase1():

    mpl = MS5607.MS5607()
    bno = BNO055.BNO055()
    bno.begin()
    time.sleep(1)
    bno.setExternalCrystalUse(True)

    checkpoint = [False, False, False]

    # ===== 初期高度を安定取得（平均化） =====
    print("Getting initial altitude...")
    alt_samples = []
    for _ in range(20):
        alt_samples.append(mpl.getAltitude())
        time.sleep(0.05)

    alt0 = sum(alt_samples) / len(alt_samples)
    print("Initial altitude:", alt0)

    # ===== 閾値設定 =====
    alt_upth = alt0 + 1.0
    alt_lowth = alt0 + 0.4

    acc0 = 17
    counter = 0
    stop_time = 100

    while True:

        # 高度も軽く平均化（5回）
        alt_samples = []
        for _ in range(5):
            alt_samples.append(mpl.getAltitude())
        alt = sum(alt_samples) / len(alt_samples)

        acc = bno.getABSAccelaration()

        print("alt:", alt)
        print("acc:", acc)
        print("checkpoint:", checkpoint.count(True))

        # ===== Check 1: 上昇検出 =====
        if (alt > alt_upth) and checkpoint.count(True) == 0:
            checkpoint[0] = True
            print("Done check0")

        # ===== Check 2: 降下検出 =====
        if (alt < alt_lowth) and checkpoint.count(True) == 1:
            checkpoint[1] = True
            print("Done check1")

        # ===== Check 3: 停止判定 =====
        if (acc < acc0) and checkpoint.count(True) == 2:
            counter += 1
            if counter > stop_time:
                checkpoint[2] = True
                print("Done check2")
        else:
            counter = 0

        if all(checkpoint):
            print("Done Phase1")
            return

        time.sleep(0.05)


if __name__ == "__main__":
    phase1()