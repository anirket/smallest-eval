from sklearn.metrics import cohen_kappa_score, confusion_matrix


def calibrate(human, judge):
    matrix = confusion_matrix(human, judge, labels=[True, False])
    tp, fn, fp, tn = matrix.ravel()
    print(f'agreement {(tp + tn) / len(human):.2f}')
    print(f'kappa     {cohen_kappa_score(human, judge):.2f}')
    print(f'TPR       {tp / (tp + fn):.2f}  (judge passed what you passed)')
    print(f'TNR       {tn / (tn + fp):.2f}  (judge failed what you failed)')
    print(matrix, '\n')


if __name__ == '__main__':
    human = [True] * 27 + [False] * 3
    calibrate(human, human)                        # identical judge: kappa 1
    calibrate(human, [True] * 30)                  # always-pass judge: agreement 0.90, kappa 0, TNR 0
    calibrate(human, [not h for h in human])       # opposite