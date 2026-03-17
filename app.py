import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="국가전략기술 예산 분석 플랫폼", layout="wide")

st.title("🇰🇷 2026년 국가 전략 기술 R&D 예산 분석")
st.sidebar.header("필터 설정")

# 1. 데이터 로드 (업로드된 파일명에 맞춰 수정)
@st.cache_data
def load_data():
    df = pd.read_csv('26-budget2.xlsx - 26년 R&D사업 통계(내역추가).csv', skip_blank_lines=True)
    # 실제 데이터 컬럼 인덱스에 기반한 전처리 필요 (C~J열 등)
    # 예시로 핵심 컬럼명 재정의
    df.columns.values[5] = '세부사업명'
    df.columns.values[6] = '내역사업명'
    df.columns.values[7] = '부처명'
    df.columns.values[9] = '예산_백만원'
    
    # 전략기술 컬럼 (K~V열에 해당하는 인덱스 선택)
    tech_cols = df.columns[10:22] 
    return df, tech_cols

df, tech_cols = load_data()

# 2. 데이터 정제: 내역사업이 있는 행만 추출하거나 세부사업 합계행만 추출하여 시각화
# 여기서는 시각화를 위해 '내역사업명'이 있는 데이터만 사용하거나 필터링 로직 구현
sub_df = df[df['내역사업명'].notna()].copy()

# 3. 사이드바 필터
selected_tech = st.sidebar.selectbox("분석할 전략 기술 분야", ["전체"] + list(tech_cols))

if selected_tech != "전체":
    display_df = sub_df[sub_df[selected_tech] > 0]
    plot_title = f"{selected_tech} 관련 사업 예산 분포"
else:
    display_df = sub_df
    plot_title = "전체 R&D 사업 예산 분포"

# 4. 시각화: 트리맵
st.subheader(plot_title)
fig = px.treemap(display_df, 
                 path=['부처명', '세부사업명', '내역사업명'], 
                 values='예산_백만원',
                 color='부처명',
                 hover_data=['예산_백만원'])
st.plotly_chart(fig, use_container_width=True)

# 5. 상세 데이터 테이블
st.subheader("세부 사업 내역")
st.dataframe(display_df[['부처명', '세부사업명', '내역사업명', '예산_백만원'] + list(tech_cols)])
