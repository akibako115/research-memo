---
created: 2026-07-06
updated: 2026-07-06
raw: "raw/papers/2026-07-06_linear_conditioning_metadata_image_segmentation.pdf"
---

# Benefits of Linear Conditioning with Metadata for Image Segmentation

この論文は，医療画像 segmentation において，vendor，acquisition parameters，patient disease type / severity，demographics，genomics などの metadata を FiLM (Feature-wise Linear Modulation) で統合する方法を検証する．segmentation methods は通常 metadata を無視するが，metadata が対象構造や task に関係する場合，feature maps への低コストな affine modulation により performance と task adaptation を改善できる．

著者らは 2D U-Net に FiLM layers を追加し，one-hot encoded metadata から channel-wise `gamma` と `beta` を生成して convolutional feature maps を modulate する．spinal cord tumor segmentation では tumor type を metadata として入れることで平均 Dice score が 5.1% 向上し，multi-organ segmentation では missing labels を持つ multi-task training に FiLM が有効であることを示した．

## 背景

医療 segmentation task は，patient condition，demographics，acquisition center，acquisition parameters などの metadata と結びついていることが多い．対象構造によっては，これらの metadata が segmentation performance を改善する prior knowledge になる．

この論文では，visual question answering で提案された FiLM を segmentation model に適用する．metadata から feature-specific affine coefficients を生成し，segmentation network の中間 feature maps を modulate することで，metadata をネットワーク内部に統合する．

## FiLMed U-Net architecture

base architecture は 2D U-Net である．model は image と one-hot encoded metadata の2入力を持つ．metadata は FiLM generator である MLP に入力され，各 FiLM layer の feature map channel ごとの `gamma` と `beta` を生成する．

FiLM generator は hidden layers 64 と16 neurons を持つ MLP であり，`gamma` と `beta` は各 convolutional feature map に対して element-wise multiplication / addition される．FiLM の computational cost は低く，image resolution に依存しない．

```text
metadata -> MLP -> gamma, beta
feature map F -> gamma * F + beta
```

preliminary experiments では，FiLM parameters の activation として sigmoid が ReLU や tanh より良かった．`gamma` が0に近いと feature を silence し，1に近いと key features を通す．FiLM layers は metadata を network に十分使わせるため，各 convolutional unit の後に置かれる．

## Experiment 1: relevant metadata を使う segmentation

spinal cord tumor segmentation dataset を用いる．dataset は 343 MRI scans で，astrocytoma 101，ependymoma 122，hemangioblastoma 120 の tumor type を持つ．tumor type は size，location，contrast intensity patterns，tissue constitution と関係するため informative な metadata として扱われる．

segmentation 対象は簡単化のため tumor core labels のみである．入力は 320 x 256 sagittal image，resolution 1mm x 1mm，metadata は tumor type である．dataset は patient 単位で 60% training，20% validation，20% testing に分け，10 random splits で学習する．

比較条件は，同じ FiLM architecture に informative metadata を入れない場合と，tumor type を metadata として入れる場合である．metadata なし条件では，同じ input vector を FiLM に渡して informative data が model に見えないようにする．

## Experiment 1 results

tumor type を prior information として入れると，Dice score が有意に改善した．

| Tumor type | No prior info | Prior info |
| --- | ---: | ---: |
| Astrocytoma | 53.3 ± 4.8 | 57.8 ± 4.9 |
| Ependymoma | 57.2 ± 3.2 | 57.7 ± 2.4 |
| Hemangioblastoma | 51.2 ± 4.0 | 61.7 ± 3.7 |
| All | 54.0 ± 2.2 | 59.1 ± 2.3 |

改善は hemangioblastomas で 10.5% (p=0.006)，astrocytomas で 4.5% (p=0.003)，all tumors combined で 5.1% (p=0.003) だった．著者らは，astrocytomas と hemangioblastomas が size，boundary，Gd-e T1w contrast enhancement などで特徴的であり，model が tumor type から segmentation に有用な prior を学習できたと説明している．

## Experiment 2: multiple tasks and missing labels

FiLM を task adaptation に使えるかを検証する．spleen，kidney，liver の organ segmentation を対象に，FiLMed model には各 scan に含まれる3 class のうち1つの segmentation だけを提示し，その class label を metadata として入力する．これにより，model は「どの臓器を segment すべきか」を metadata から知る．

datasets は Medical Segmentation Decathlon の spleen / liver scans と KiTS19 の kidney scans から作られる．spleen dataset が41 scans だったため，kidney と liver も最初の41 scans に絞る．training example は 512 x 512 axial slice と available label の組であり，patient 単位で 60% training，20% validation，20% testing に分ける．

small / unbalanced dataset の実験では，spleen と kidney の2 class を使い，一方の class の subject 数を 2, 4, 6, 8, 12 と変え，もう一方は12 subjects に固定する．train/validation subjects を合わせた size であり，least subject class に対して test set 25 subjects で評価する．

## Experiment 2 results

FiLMed multi-class model は，各 scan で1つの organ label しか与えられない missing-label setting でも，single-class U-Nets と同等の performance に到達した．同じ missing-label dataset で FiLM なしの multi-class 2D U-Net を学習すると，全 class 平均 Dice 41.7 ± 16.0 と悪く，partial segmentation しかできなかった．

| Task | Multi-class 2D U-Net | Single-class 2D U-Net | Multi-class FiLMed U-Net |
| --- | ---: | ---: | ---: |
| Liver | 50.3 ± 18.3 | 95.1 ± 1.4 | 94.1 ± 1.6 |
| Spleen | 35.6 ± 14.2 | 91.7 ± 6.3 | 92.2 ± 5.3 |
| Kidney | 39.2 ± 13.1 | 90.4 ± 9.3 | 90.7 ± 8.1 |

small / unbalanced dataset では，同じ数の labels がある条件で，FiLMed models は regular U-Nets より高い Dice score を示した．dataset size 2, 4, 6, 8 では，それぞれ 11.5%，16.7%，5.5%，4.7% の改善があった．これは，FiLMed model が他 task の画像から学習できたことを示す．

## Discussion

FiLM は prior knowledge を統合する柔軟で low computational cost な方法である．この論文では spinal cord tumor type を proof of concept として用いたが，metadata には acquisition center，scanner vendor，anatomical location，pose estimation，disease type / severity，rater experience / rater id なども含められる可能性がある．

FiLM は，どの annotation が提示されているかを model に知らせることで missing labels に対応できる．多くの医療画像 dataset は scope と annotation が限られるが，FiLM を使うと，各 dataset に1 class しか annotation がなくても，複数 dataset から single multi-class model を作れる．task 間で weights が共有されるため，annotation 数を減らしつつ transfer learning が起こる．

ただし，metadata は one-hot encoded されるため，この論文の実装では discrete prior information が必要である．continuous data，たとえば age，size，MRI acquisition parameters は binned range に discretize する必要がある．future work として，echo-time や flip angle などの MRI acquisition parameters を統合し，acquisition sequence に agnostic な model を作ることが挙げられている．

## 関連概念

- [[FiLM]]
- [[Image_Tabular_Fusion]]
- [[Conditional_Modulation]]
- [[Metadata_Conditioning]]
- [[Medical_Image_Segmentation]]
