---
created: 2026-07-06
updated: 2026-07-06
sources:
  - "[[sources/2026-07-06_fairread_demographic_refusion_medical_image_classification]]"
  - "[[sources/2026-07-06_fcro_multiple_sensitive_attributes_medical_image_classification]]"
---

# FairREAD

医療画像 fairness では，sensitive attribute を model から取り除けばよい，とは限らない．age，sex，race などは bias の経路にもなるが，疾患の prevalence や manifestation と関係する臨床情報でもある．FairREAD は，画像表現から demographic shortcut を一度取り除き，その後 demographic attributes を controlled に再注入する fairness-aware fusion 手法である．

この手法が必要になるのは，[[Race_Recognition_In_Medical_Images]] が示すように，image-only model でも sensitive information を内部に持ちうるからである．FairREAD は，画像由来の潜在的 shortcut と，明示的に与えた demographic attributes の臨床的利用を分けて扱う．

## 全体像

FairREAD は Re-fusion After Disentanglement という名前の通り，2段階の考え方を持つ．

```text
image
  -> fair image encoder
  -> demographic-invariant image representation
  -> controlled re-fusion with demographic attributes
  -> disease prediction
  -> subgroup-specific threshold
```

| Component | 何をするか |
| --- | --- |
| Fair Image Encoder | image representation から demographic information を消す |
| Orthogonality loss | target representation と sensitive representation を分離する |
| Adversarial loss | latent vector から demographic attributes を予測できないようにする |
| Re-fusion block | demographic attributes で latent representation を rescale する |
| Min-gap threshold | subgroup ごとに TPR/TNR gap が小さい threshold を選ぶ |

## なぜ除去してから再注入するか

sensitive information を完全に除去すると，spurious correlation は減るかもしれないが，臨床的に有用な情報も失われる可能性がある．たとえば age や sex は疾患 prevalence と関係し，race や gender も社会的・医療制度的な要因を通じて disease distribution や label quality と関係しうる．

FairREAD はこの問題を，情報の由来を分けることで扱う．

| 情報の経路 | リスク | FairREAD の扱い |
| --- | --- | --- |
| image representation 内の demographic signal | shortcut / hidden bias として使われる | disentanglement で除去する |
| explicit demographic attributes | 臨床的に有用な context を持つ | re-fusion で controlled に使う |
| final decision threshold | subgroup ごとの operating point 差 | Min-gap threshold で調整する |

この設計は，protected attribute を単に隠すのではなく，どの経路で使われるかを制御する発想である．

[[FCRO]] は，FairREAD の前段にある orthogonal representation learning の代表例である．FCRO は target representation と sensitive representation を column / row space の両方で orthogonal にする．FairREAD はこの発想を fair image encoder に使いつつ，明示的な demographic attributes を re-fusion する点が異なる．

## Re-fusion は何をしているか

FairREAD の re-fusion block は，demographic attributes を MLP に通して `mu` と `sigma^2` を作り，fair image representation を latent space で rescale する．これは，tabular attributes によって image feature を条件付ける [[Image_Tabular_Fusion]] の一種として読める．

```text
z_T = FairImageEncoder(image)
mu, sigma^2 = MLP(demographic_attributes)
z_fused = z_T * Proj^-1(sigma^2 * Proj(z_T) + mu)
```

この構造は [[FiLM]] に近い feature-wise modulation として理解できる．ただし目的は単なる性能向上ではなく，demographic shortcut を取り除いた後に，明示属性を制御された形で使い直すことである．

## Subgroup-specific threshold

FairREAD は，training 後の threshold も subgroup ごとに調整する．Min-gap strategy では，subgroup `g` ごとに TPR と TNR の差が最小になる threshold を選ぶ．

```text
theta_g = argmin |TPR_g - TNR_g|
```

これは [[Equalized_Odds]] と関係する operating-point adjustment である．AUC が高くても threshold が不適切なら subgroup 間の decision disparity は残るため，FairREAD は representation learning と threshold adjustment を組み合わせる．

## 評価で見るべき点

FairREAD の評価では，accuracy や AUC だけでなく，fairness metric と trade-off metric を見る．

| 指標 | 意味 |
| --- | --- |
| AUC | threshold-free diagnostic performance |
| Delta AUC | subgroup 間の AUC disparity |
| Delta EO | subgroup 間の Equalized Odds disparity |
| FATE_EO | accuracy と Delta EO の trade-off quality |
| FATE_AUC | AUC と Delta AUC の trade-off quality |

CheXpert 実験では，FairREAD は平均 AUC 0.839，Delta EO 0.129，FATE_EO 0.196，FATE_AUC 0.197 を示し，accuracy 以外の平均 metric で baselines を上回った．これは，fairness-aware fusion が診断性能を保ちながら subgroup disparity を減らせる可能性を示す．

## 限界

FairREAD は demographic attributes を binary に discretize している．これは sample size を確保するには実用的だが，subgroup 内の heterogeneity や intersectional unfairness を隠す可能性がある．また，subgroup-specific threshold は deployment で demographic attributes が利用可能であることを前提にする．

したがって FairREAD を評価するには，次の点を確認する必要がある．

| 確認点 | 理由 |
| --- | --- |
| attributes の missingness | threshold / re-fusion が属性に依存するため |
| intersectional subgroup performance | binary subgroup 内に残る unfairness を見るため |
| OOD fairness | CheXpert で良くても MIMIC-CXR で崩れる可能性があるため |
| calibration | subgroup-specific threshold の安全性に関係するため |

## リファレンス

| 用語 | 意味 |
| --- | --- |
| FairREAD | Fair Re-fusion After Disentanglement |
| Fair Image Encoder | demographic information を除いた image representation を作る encoder |
| re-fusion | demographic attributes を latent representation に再注入する処理 |
| Min-gap threshold | subgroup ごとに TPR/TNR gap を最小化する threshold |
| FATE | performance と fairness の trade-off quality を測る metric |

## 関連概念

- [[Image_Tabular_Fusion]]
- [[FiLM]]
- [[FCRO]]
- [[Medical_Image_Fairness_Evaluation]]
- [[Equalized_Odds]]
- [[Demographic_Imbalance]]
- [[Race_Recognition_In_Medical_Images]]
