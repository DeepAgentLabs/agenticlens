---
name: Obsidian Telemetry
colors:
  surface: '#10131a'
  surface-dim: '#10131a'
  surface-bright: '#363941'
  surface-container-lowest: '#0b0e15'
  surface-container-low: '#191b23'
  surface-container: '#1d1f27'
  surface-container-high: '#272a32'
  surface-container-highest: '#32353d'
  on-surface: '#e1e2ec'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#e1e2ec'
  inverse-on-surface: '#2d3038'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#ffb95f'
  on-tertiary: '#472a00'
  tertiary-container: '#e29100'
  on-tertiary-container: '#523200'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#10131a'
  on-background: '#e1e2ec'
  surface-variant: '#32353d'
typography:
  headline-xl:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.025em
  headline-xl-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 15px
    fontWeight: '600'
    lineHeight: 22px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 18px
  label-telemetry:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.01em
  label-code-caps:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.06em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style
The design system articulates an ultra-premium, dark cockpit telemetry and clinical observability environment tailored for autonomous clinical operations. It merges mission-critical healthcare compliance with the precision and responsiveness of modern developer observability platforms like Linear and Datadog.

The visual direction centers on **Technical Glassmorphism & Cybernetic Precision**. Surfaces are forged from deep obsidian and midnight slate layers, punctuated by hair-thin luminous borders, radial ambient backlight glows, and surgical status accents. Every element is designed to evoke absolute institutional trust, high-throughput cognitive efficiency, and high-stakes clarity. Autonomous agentic steps require explicit human verification gates; thus, the interface balances automated stream velocity with unmistakable checkpoints, tactical monospaced data readouts, and rich clinical-state contrast.

## Colors
The palette leverages a low-reflective foundation that reduces visual fatigue during high-density triage shifts, offset by hyper-focused luminescent markers.

- **Canvas & Surface Architecture**:
  - `canvas-root`: `#0a0d14` (Deep obsidian background)
  - `surface-base`: `#0f1422` (Midnight slate primary card backgrounds)
  - `surface-elevated`: `#141b2d` (Telemetry panels, drawer overlays, popovers)
  - `surface-inset`: `#07090f` (Code/telemetry terminal wells and code inspection fields)
  - `surface-glass`: `rgba(15, 20, 34, 0.72)` with `backdrop-filter: blur(16px)`

- **Accent & State System**:
  - `primary` (`#10b981` / `#34d399`): Autonomous execution, approved prior authorizations, safe system states, verification completions.
  - `secondary` (`#06b6d4` / `#38bdf8`): Agentic telemetry streams, active API calls, dynamic vector matching, running pipelines.
  - `warning` (`#f59e0b` / `#fbbf24`): Human-in-the-loop intervention gates, clinical discrepancy flags, pending payer requirements.
  - `danger` (`#f43f5e` / `#fb7185`): Prior auth denials, missing medical necessity criteria, fatal webhook exceptions.
  - `border-subtle`: `rgba(255, 255, 255, 0.08)`
  - `border-vibrant`: `rgba(16, 185, 129, 0.35)` (Focus, agent sync state)

- **Typography & Content Hierarchy**:
  - `text-high-contrast`: `#f8fafc`
  - `text-secondary`: `#94a3b8`
  - `text-muted`: `#64748b`
  - `text-code-glow`: `#38bdf8`

## Typography
The system enforces a dual-type architecture:
- **Operational & Interface Core (Plus Jakarta Sans & Inter)**: Plus Jakarta Sans lends modern, authoritative structure to page headers and high-level card titles without geometric exaggeration. Inter governs system controls, narrative clinical notes, modal copies, and interactive switches with maximum legibility across dense data matrices.
- **Precision Data Core (JetBrains Mono)**: Reserved for programmatic and medical taxonomy. CPT/HCPCS codes, ICD-10 identifiers, prior auth tracking tokens, payer NPIs, microsecond latency timestamps, and agentic confidence percentages are rendered strictly in `JetBrains Mono` with tabular numerals enabled (`tnum`, `zero`) to ensure perfect vertical alignment across scanning vectors.

## Layout & Spacing
The layout implements a high-density, multi-pane telemetry grid anchored by fixed navigational rails and adaptive payload canvas regions.

- **Grid Architecture**:
  - **Desktop (HM
J����X��[[�\�[[Y]�X�^[�]�][���\�\��YX�ۈ�Z[H͌�\�][ۘ[]Y]YH�YX�\�
�[܈]]�\�\��[\�Y�HY�[��XY�HY\�K[�X��[[�XZ[�؜�\��X�[]H	�R�[�Yܘ][ۈ�[��\�[�H��\�X�H�Y�[�X�[[Y]�H�X�H�]�\���H
��X�]
͎HM�\
J����X��[[�^[�]��XY�H]Y]YH�[�ٛܛ\�[��[�^[�X�H��^N�Y�[�X��X�H�]�\�Y�][��[�ٙ�X�[��\��YK[�]�Y]��H
��[ؚ[H
͎
J���KX��[[��\�ۜ�]�H��X[N�Y�\�[ܚ]H[X[�Y�]Hݙ\��YHX�[ۜ�[��܈�H\��\�[����HX�[ۈ�Y]���H
���]H	�Y]�X�ʊ���H�[�\��\�[[�H�X�YܚY�۝���[��\�Y[��[���\ۙ[�����[�ˈ��\X�[��H�\�X�[X��[��
�X�K^���X�K\�X
H\��]�ܙY�܈��H�Y�\��ۙ�Y[��H�\��[�Y]�X�[��[H�\��۝Z[�\��][^�H�[�\��\�[�\��[�\\�][ۈ
�X�K[�
H��[[��H[[Y]�H[��]H�]��ۚ]]�H�[[�\�˂����[]�][ۈ	�\�\\�ܙX]Y��Y�[Z[�\��[��H[��X�[�X�]H�]\�[�X]�H���Y��΂��H
��ۘ[^Y\�[�ʊ��[[Y[���X��\�\����HH�[��\�
�LM
H�[�\�YYX]H�\��X�\�
��M��
H���][��[��X�[�[�
�MX��
K�XX�]�[[�ܙX\�\��Y�H[�Y��\��[��X�Z]�\�[�[�ܙX\�Y�X�[\��[HY���H
���\��[ܜ\�H	��ܙ\�ʊ��[�[�ݙ\�[�[�[��X��H[[Y]�H�\��\�H�ؘJMK����JX�]M��X����X�\�[�H[�Y�YY\����Hو�ؘJ�MK�MK�MK�
X��H
���X�[\�[��]�YX[��J����[Z][H[[Y]�H�\��[��ܜܘ]H[�[��]�ܘYY[���[�X\�YܘYY[�
NY��ؘJ�MK�MK�MK��H	K�ؘJ�MK�MK�MK
HL	JX��H
��[X�Y[��YX[�X��Y�
���X�]�HY�[��\�][ۜ�[�Y�\�[ܚ]H�]\��ڙX��X�KY��\�Y�YX[�X��Y���Z[�Z\���[�[����\΂�HY�[��[��[�Έ�YX[YܘYY[�
[\�H]��[�\��ؘJ�N��L��L�H	K�[��\�[��	JX�H\�ݘ[�]N��YX[YܘYY[�
[\�H]��[�\��ؘJM�NKL�K�L�H	K�[��\�[��	JX�HX�[ۈ�\]Z\�Y��Y��Y��YX[YܘYY[�
[\�H]��[�\��ؘJ�KMNLK�M
H	K�[��\�[��	JX�����\\H\�Yۈ�\�[H[\�\�H
���ٝ
]�[JJ���[�Y]�X��۝�\���H�[X\�H�\��X�H�\��X[���[���H[��X�܈[�[�\�H�\�[X
��[�Y[�
H�XZ[�Z[�HX��X�[�X[�X�]\��]X�\�[��[�\�K��H[�\�X�]�H��]�\�X�[\��[�[�]ܘ\\��[�[�[�H��H�����\�H��\�[X
��[�YX�\�X
K��H[�[�ZXܛ��]\��Y�\�]�X]H[�[�[ۘ[H�
���[�Y]\�
��[�YY�[
J���ݚY[��[[YYX]H�\�X[�۝�\��]�Y[�H�Y�Y��X�\�[ܚY[�ܙ�[�X��]\��]\˂������\ۙ[������]ۜ�	�[�\�X�]�H�۝��H
���[X\�H�]]ܚ^�HX�[ۊ���[Y\�[�\�H
�L�NX
KY�X�۝�\�\��^
�L�LM�
K�۝�ZY���]H�X�H�]\����ۈݙ\�
��\�Y�ΈM��ؘJM�NKL�K�
X
K��H
���X�ۙ\�H�[[Y]�HX�[ۊ����\���\��X�H
�ؘJ�MK�MK�MK�
X
K\�ܙ\�و�ؘJ�MK�MK�MK�L�X^َ�Y���ݙ\��Y��\���X��ܛ�[��ؘJ�MK�MK�MK�
X��H
��[X[�Q�]H[�\��[�[ۈ�]ۊ���[X�\��][�H
�ؘJ�KMNLK�
X
H�][�[X]Y��X][��\�[Y]\�[�H�[�[�Y�[�X��[��\]Z\�\�[[YYX]H�[�X�X[��[Y][ۋ�������]\�[�	��ۙ�Y[��H�Y�\H[\�\Y
NNN\
H�Y�\��۝Z[�[��[�]]ۛ�[�\�[[Y]�H[�H�
��\��H�]X]�[����܈]\�JK��H
��\�ݙY��XYJ����X��ܛ�[��ؘJM�NKL�K�L�X^���NX�ܙ\��ؘJM�NKL�K��JX��H
��Y�[�[�[^�[�ʊ���X��ܛ�[��ؘJ�N��L��L�X^�����ܙ\��ؘJ�N��L���JX��H
���ۙ�Y[��HY]\����[�[�H�\��ۜ�\�[��وH�Y�Y[�Y�X���]H�X�\�Y[Y\�[܈�X[��[\�^Z[��^X�\��[�Y�\�[��]��Z[��[ۛ�
K�ˋNK�	H�ӑ�
K������X�[\�[[Y]�H	�\�HX�H�����X]\�H�\��]\�[�ܙ\��YY�]Z\�[�H]�Y\��
�ؘJ�MK�MK�MK�JX
K��Hݙ\�[��H���ZY[��X�H[[Z[�][ۈ
�MX��
H[��[�\���۝^X[X�[ۈ[�
K�ˋ[��X��X�X�\\���]X�ܘ�H�[��
K��H�[�X�[��\�
�NL�M����X��\�H\�H��[YY[�ZXܛ�Y���[Y�]�\��X�KZ[��][�[ۛ��X�Y\�ܘ\K�������ܛH[�]�	���H[��X��[H^�Y[�][^�H�\��X�KZ[��]
��L�
H�]HY�][�ܙ\��ؘJ�MK�MK�MK�
X����\��]\��Y��\�[�[X��X��X[����
\������\�Y�ΈL��ؘJ�N��L���X
K��HY�[����Y]�\��[\[Y[�H[ۛ��X�Y\�Z[�[�[[���]�X�H���[�^[���[�^ZY�Y�Y��ӈ�[�X�[�[[X\�Y\�[�[�[ZX�[Y\�[\��[�\�˂������X�X[^�Y��\ۙ[��[X[�Z[�]KS���\�Y�X�][ۈ�]B�HYX�]Y�]XX�[ۈ�\��X]\�[��HX[\�Y�H��ܙ\���X�ΈY�\�][ۈ\�^\�HRHY�[�	���[[X\�^�Y�[�X�[�][ۘ[H�]�]YR��ZY[[�\���Y�\�][ۈ�\�\�Hܞ\�ܘ\X��Yۘ]\�H�Y��\�\�X�X[�ݙ\��YH���\�[�[��[�R�\��]ۋ