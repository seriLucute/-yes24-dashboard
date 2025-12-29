import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os

# 페이지 설정
st.set_page_config(
    page_title="Yes24 도서 데이터 대시보드",
    page_icon="📚",
    layout="wide",
)

# 커스텀 CSS (프리미엄 UI/UX 느낌을 위한 스타일링)
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
    }
    .insight-box {
        background-color: #e9ecef;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #3498db;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 0.95rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    file_path = "yes24_books.csv"
    if not os.path.exists(file_path):
        # 작업 디렉토리가 다를 경우를 대비해 절대 경로 확인 필요할 수 있음
        # 여기서는 같은 폴더에 있다고 가정
        pass
    
    df = pd.read_csv(file_path)
    
    # 수치형 데이터 변환
    numeric_cols = ['판매가', '정가', '평점', '리뷰수', '판매지수']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    return df

df_raw = load_data()

# 사이드바 구성
st.sidebar.title("🔍 대시보드 메뉴")
menu = st.sidebar.selectbox(
    "이동할 페이지를 선택하세요",
    ["🏠 Dashboard Home", "📈 Sales Analysis", "🏢 Publisher Insights", "🔍 Search Explorer", "📊 Raw Data Viewer"]
)

st.sidebar.markdown("---")
st.sidebar.header("📊 글로벌 필터")

# 가격 범위 필터
min_price = float(df_raw['판매가'].min())
max_price = float(df_raw['판매가'].max())
price_range = st.sidebar.slider(
    "가격 범위 (원)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=1000.0
)

# 평점 범위 필터
rating_range = st.sidebar.slider(
    "평점 범위",
    min_value=0.0,
    max_value=10.0,
    value=(0.0, 10.0),
    step=0.1
)

# 필터링 적용
df = df_raw[
    (df_raw['판매가'] >= price_range[0]) & 
    (df_raw['판매가'] <= price_range[1]) &
    (df_raw['평점'] >= rating_range[0]) &
    (df_raw['평점'] <= rating_range[1])
]

# 1. Dashboard Home
if menu == "🏠 Dashboard Home":
    st.title("🏠 Yes24 IT 도서 시장 요약")
    st.markdown("전체 수집된 도서 데이터의 핵심 지표를 한눈에 확인하세요.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("총 도서 수", f"{len(df)} 권", delta=None)
    with col2:
        st.metric("평균 판매지수", f"{int(df['판매지수'].mean()):,} 점")
    with col3:
        st.metric("최고가 도서", f"{int(df['판매가'].max()):,} 원")
    with col4:
        st.metric("평균 평점", f"{df['평점'].mean():.2f} 점")
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("출판사별 도서 수 TOP 10")
        pub_counts = df['출판사'].value_counts().head(10).reset_index()
        pub_counts.columns = ['출판사', '도서 수']
        fig = px.bar(pub_counts, x='도서 수', y='출판사', orientation='h', 
                     color='도서 수', color_continuous_scale='Blues',
                     template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("도서 평점 분포")
        fig = px.histogram(df, x='평점', nbins=20, 
                           color_discrete_sequence=['#3498db'],
                           template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 📝 데이터 요약 통계")
    st.dataframe(df.describe().T.style.format("{:.2f}"), use_container_width=True)

# 2. Sales Analysis
elif menu == "📈 Sales Analysis":
    st.title("📈 판매지수 심층 분석")
    
    tab1, tab2, tab3 = st.tabs(["Top Sales", "Price Analysis", "Rating Analysis"])
    
    with tab1:
        st.subheader("🏆 판매지수 TOP 20 도서")
        top_20 = df.nlargest(20, '판매지수')
        
        fig1 = px.bar(top_20, x='판매지수', y='제목', orientation='h',
                     title="판매지수 상위 20개 도서",
                     color='판매지수', color_continuous_scale='Viridis',
                     hover_data=['출판사', '판매가'],
                     template='plotly_white')
        fig1.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.pie(top_20, names='출판사', values='판매지수',
                     title="TOP 20 도서의 출판사별 판매지수 점유율",
                     hole=0.4, template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        이 그래프는 현재 Yes24 IT 카테고리에서 가장 높은 반응을 얻고 있는 상위 20개 도서를 보여줍니다. 
        분석 결과, 상위권 도서들은 단순히 높은 판매량뿐만 아니라 특정 출판사(예: 이지스퍼블리싱, 골든래빗 등)에 집중되어 있는 경향을 보입니다. 
        특히 판매지수 1위를 기록한 도서는 평균적인 도서들에 비해 월등히 높은 지수를 보여주며 시장을 선도하고 있습니다. 
        하단의 피벗 테이블을 통해 각 도서의 상세 판매가와 평점을 대조해보면, 높은 평점이 반드시 최고의 판매지수로 이어지지는 않으나 
        신뢰도를 형성하는 중요한 지표임을 알 수 있습니다.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### [표] 상위 20개 도서 상세 데이터")
        st.table(top_20[['제목', '출판사', '판매지수', '판매가', '평점']].head(10))
        
    with tab2:
        st.subheader("💰 가격과 판매지수의 상관관계")
        
        fig1 = px.scatter(df, x='판매가', y='판매지수', 
                         size='리뷰수', color='평점',
                         hover_name='제목',
                         title="가격 vs 판매지수 산점도 (크기: 리뷰수, 색상: 평점)",
                         template='plotly_white')
        st.plotly_chart(fig1, use_container_width=True)
        
        # 가격대별 평균 판매지수
        df['가격대'] = pd.cut(df['판매가'], bins=[0, 10000, 20000, 30000, 40000, 100000], 
                           labels=['1만 이하', '1~2만', '2~3만', '3~4만', '4만 초과'])
        price_group = df.groupby('가격대')['판매지수'].mean().reset_index()
        
        fig2 = px.line(price_group, x='가격대', y='판매지수', markers=True,
                      title="가격대별 평균 판매지수 추이",
                      template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        도서 가격과 판매지수 사이의 관계를 분석한 결과, 주로 2만 원에서 3만 원 사이의 가격대 도서들이 가장 활발하게 소비되고 있음을 알 수 있습니다. 
        산점도를 보면 고가의 도서(4만 원 이상)는 판매지수가 상대적으로 낮은 분포를 보이지만, 충성도가 높은 특정 기술 서적의 경우 리뷰 수가 많고 평점도 높게 유지되는 독특한 양상을 보입니다. 
        따라서 IT 도서 시장에서는 '가성비' 모델과 '전문성' 모델이 뚜렷하게 구분되며, 일반적인 입문서는 중저가 정책이 판매 지수 상승에 유리한 것으로 판단됩니다.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### [표] 가격대별 판매지수 및 평점 피벗 테이블")
        price_pivot = df.pivot_table(index='가격대', values=['판매지수', '평점'], aggfunc='mean')
        st.dataframe(price_pivot.style.format("{:.2f}"), use_container_width=True)

    with tab3:
        st.subheader("⭐ 평점과 리뷰수가 판매에 미치는 영향")
        
        fig1 = px.box(df, x='평점', y='판매지수', 
                      title="평점 점수별 판매지수 분포",
                      color='평점', template='plotly_white')
        st.plotly_chart(fig1, use_container_width=True)
        
        fig2 = px.scatter(df, x='리뷰수', y='판매지수', 
                         trendline="ols",
                         title="리뷰 수와 판매지수의 선형 상관관계",
                         template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("""
        <div class="insight-box">
        리뷰 수와 판매지수 간에는 매우 강력한 양의 상관관계가 관찰됩니다. 이는 리뷰가 많이 쌓일수록 사회적 증거(Social Proof)로 작용하여 신규 구매자의 유입을 촉진하는 선순환 구조를 형성하고 있음을 시사합니다. 
        반면 평점의 경우, 9.5점 이상의 매우 높은 점수 구간에서 판매지수의 편차가 크게 나타나는데, 이는 하이엔드 기술 서적이 소수의 독자로부터 높은 평가를 받더라도 대중적인 판매량으로 바로 연결되지는 않음을 의미합니다. 
        하지만 평점이 낮은 도서는 판매지수 또한 급격히 하락하는 경향이 있어, 일정 수준 이상의 퀄리티 유지는 시장 생존의 필수 조건이라 할 수 있습니다.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### [교차표] 평점 구간별 도서 수 및 평균 리뷰 수")
        df['평점구간'] = pd.cut(df['평점'], bins=[0, 8, 9, 9.5, 10], labels=['8점미만', '8~9점', '9~9.5점', '9.5~10점'])
        rating_ct = pd.crosstab(df['평점구간'], columns='count')
        rating_ct['평균리뷰수'] = df.groupby('평점구간')['리뷰수'].mean()
        st.dataframe(rating_ct.style.format({"count":"{:.0f}", "평균리뷰수":"{:.2f}"}), use_container_width=True)

# 3. Publisher Insights
elif menu == "🏢 Publisher Insights":
    st.title("🏢 출판사 및 시장 점유율 분석")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("출판사별 누적 판매지수 TOP 10")
        pub_sales = df.groupby('출판사')['판매지수'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(pub_sales, x='판매지수', y='출판사', orientation='h',
                     color='판매지수', color_continuous_scale='Reds',
                     template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("출판사별 평균 평점 vs 평균 가격")
        pub_stats = df.groupby('출판사').agg({
            '평점': 'mean',
            '판매가': 'mean',
            '판매지수': 'count'
        }).rename(columns={'판매지수': '도서수'}).reset_index()
        
        fig = px.scatter(pub_stats[pub_stats['도서수'] > 2], 
                         x='판매가', y='평점', size='도서수',
                         text='출판사', title="평균 지표 산점도 (3권 이상 출판사 대상)",
                         template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    <div class="insight-box">
    출판사별 시장 점유율 분석 결과, 특정 상위 3~5개 출판사가 전체 IT 도서 매출 지표의 상당 부분을 점유하고 있는 과점 형태의 시장 구조를 보이고 있습니다. 
    이지스퍼블리싱과 골든래빗은 높은 누적 판매지수를 기록하며 대중적인 인기를 얻고 있는 반면, 한빛미디어와 길벗은 방대한 도서 라인업(포트폴리오)을 바탕으로 안정적인 시장 지배력을 유지하고 있습니다. 
    산점도 분석을 통해 각 출판사의 포지셔닝을 파악해 보면, 고가의 전문 서적을 주로 출간하면서도 높은 평점을 유지하는 '프리미엄 브랜드'와 트렌디한 주제를 합리적인 가격에 빠르게 공급하는 '트렌드 세터 브랜드'로 나뉘어 있음을 확인할 수 있습니다.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("#### [표] 주요 출판사 성과 지표 요약 (누적 판매순)")
    st.dataframe(pub_stats.sort_values('도서수', ascending=False).head(15).style.format({"평점":"{:.2f}", "판매가":"{:.0f}"}), use_container_width=True)

# 4. Search Explorer
elif menu == "🔍 Search Explorer":
    st.title("🔍 도서 검색 익스플로러")
    
    with st.expander("🔎 상세 검색 조건 설정", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            all_pubs = sorted(df_raw['출판사'].unique())
            search_pub = st.multiselect("출판사 선택", options=all_pubs, default=[])
        with c2:
            search_key = st.text_input("제목/부제목 키워드 입력", "")
    
    # 검색 필터 적용
    search_df = df.copy()
    if search_pub:
        search_df = search_df[search_df['출판사'].isin(search_pub)]
    if search_key:
        search_df = search_df[
            search_df['제목'].str.contains(search_key, case=False, na=False) | 
            search_df['부제목'].str.contains(search_key, case=False, na=False)
        ]
    
    st.markdown(f"**검색 결과:** 총 {len(search_df)} 권의 도서가 발견되었습니다.")
    
    if not search_df.empty:
        # 검색 결과 시각화
        c1, c2 = st.columns(2)
        with c1:
            fig = px.scatter(search_df, x='판매가', y='판매지수', color='출판사',
                             hover_name='제목', title="검색 결과 내 가격 vs 판매지수",
                             template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.bar(search_df.head(10), x='판매지수', y='제목', 
                         title="검색 결과 상위 10권", template='plotly_white')
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(search_df[['제목', '부제목', '출판사', '판매가', '평점', '판매지수']], use_container_width=True)
    else:
        st.warning("검색 기준에 부합하는 도서가 없습니다. 필터를 조정해 보세요.")

# 5. Raw Data Viewer
else:
    st.title("📊 Raw Data Viewer")
    st.markdown("수집된 원본 데이터를 확인하고 필터링된 결과를 다운로드할 수 있습니다.")
    
    st.info(f"현재 사이드바 필터가 적용된 행 수: {len(df)} / 전체 행 수: {len(df_raw)}")
    
    st.dataframe(df, use_container_width=True)
    
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 필터링된 데이터 CSV 다운로드",
        data=csv,
        file_name='yes24_filtered_data.csv',
        mime='text/csv',
    )
    
    st.markdown("---")
    st.markdown("### 📈 데이터 정보")
    st.write(df.dtypes.to_frame(name='Data Type'))
