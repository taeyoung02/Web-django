from sklearn.model_selection import train_test_split
import pickle
from .models import Post, Category, UploadFileModel
from django.views.generic import ListView, DetailView, UpdateView

from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .forms import UploadFileForm

import pandas as pd
import urllib
import os
from django.http import HttpResponse, Http404
import mimetypes


class PostList(ListView):
    model = Post
    paginate_by = 5

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()

        return context


class PostSearch(PostList):
    def get_queryset(self):
        q = self.kwargs['q']
        object_list = Post.objects.filter(Q(title__contains=q) | Q(content__contains=q))
        return object_list

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostSearch, self).get_context_data()
        context['search_info'] = 'Search: "{}"'.format(self.kwargs['q'])
        return context


class PostDetail(DetailView):
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()

        return context


def ml():
    import numpy as np  # numpy : numeric python. numeric 방법 라이브버리. 수치해석.
    import pandas as pd  # panadas: 데이터 프레임 쉽게 다룰 수 있게 해주는 함수 포함.

    # ignore warnings
    import warnings
    warnings.filterwarnings("ignore")  # 경고창 무시.

    # 원본 파일 불러오기
    telcom = pd.read_excel("C:/telco-customer-churn/gwa_ver1.1.xlsx")
    telcom1 = pd.read_excel("C:/telco-customer-churn/gwa_ver2.xlsx")

    telcom = pd.concat([telcom, telcom1]);

    # 열 이름에 있는 띄어쓰기 제거
    telcom.rename(columns=lambda x: x.replace(' ', ''), inplace=True)

    # 열 이름에 있는 띄어쓰기 제거
    # 요금항목명의 데이터가 가지는 띄어쓰기 값 삭제.
    if '임대이용료                              ' in telcom['요금항목명'].unique():
        telcom['요금항목명'] = telcom['요금항목명'].replace('임대이용료                              ', '임대이용료')
    if '유지보수료                              ' in telcom['요금항목명'].unique():
        telcom['요금항목명'] = telcom['요금항목명'].replace('유지보수료                              ', '유지보수료')
    if '장비구매료                              ' in telcom['요금항목명'].unique():
        telcom['요금항목명'] = telcom['요금항목명'].replace('장비구매료                              ', '장비구매료')
    if '신규설치비                              ' in telcom['요금항목명'].unique():
        telcom['요금항목명'] = telcom['요금항목명'].replace('신규설치비                              ', '신규설치비')
    if '컨설팅료                                ' in telcom['요금항목명'].unique():
        telcom['요금항목명'] = telcom['요금항목명'].replace('컨설팅료                                ', '컨설팅료')
    if '신규설치비                     ' in telcom['요금항목명'].unique():
        telcom['요금항목명'] = telcom['요금항목명'].replace('신규설치비                     ', '신규설치비')

    # 데이터에 오류있는 17년 7월 데이터 삭제
    # 들어오는 데이터에는 17년 7월이 없을 것이므로 삭제

    # 이부분은 애초에 존재하는 columns이므로 if문 안함
    telcom.drop(['선납금액', '기타요금', '연체료', '감액료',
                 '당월금액', '청구금액'], axis='columns', inplace=True)

    # 0의 값 가지는 특성 삭제
    idx = telcom[(telcom['요금항목명'] == 0) |
                 (telcom['요금항목명'] == '신규설치비') |
                 (telcom['요금항목명'] == '장비구매료') |
                 (telcom['요금항목명'] == '컨설팅료') |
                 (telcom['요금항목명'] == '해지위약료') |
                 (telcom['요금항목명'] == '이전비')].index
    telcom = telcom.drop(idx)
    # 연속성 없는 열과 NULL 삭제
    telcom = telcom.reset_index()[telcom.columns]  # 인덱스 재설정

    # 청구일자에서 미리 최대값을 저장
    date_max = telcom['청구일자'].max()

    # 차월증감액 삭제
    del telcom['차월증감액']
    telcom = telcom.reset_index()[telcom.columns]  # 인덱스 재설정

    # 할인율 특성 추가
    telcom = telcom.assign(할인율=lambda x: (x['할인금액'] / x['금액']) * 100)
    telcom = telcom.fillna(0)

    grouped1 = telcom['금액'].groupby(telcom['서비스계약ID'])
    grouped2 = telcom['할인율'].groupby(telcom['서비스계약ID'])

    bill = grouped1.mean().reset_index(name="평균금액")

    discount = grouped2.mean().reset_index(name="평균할인율")

    df = pd.concat([bill, discount], axis=1)

    df.drop('서비스계약ID', axis=1, inplace=True)

    # 서비스 계약 ID 같은 놈들끼리 금액을 합침.
    # 합친 놈들의 '평균금액'열 새로 생성
    # 합친 놈들의 '평균할인율'열 새로 생성
    # 서비스계약ID 제거하여 평균금액과 평균할인율만 남김.

    telcom.sort_values(by=['청구일자'], axis=0, inplace=True)

    telcom = telcom.drop_duplicates(["서비스계약ID"], keep='last')

    telcom.sort_values(by=['서비스계약ID'], axis=0, inplace=True)

    telcom = telcom.reset_index()[telcom.columns]  # 인덱스 재설정

    # 청구일자 별로 정렬한 뒤 마지막 제외 중복된 계약ID 행 모두 삭제.
    # 가장 마지막에 낸 금액만 남겨짐.
    # 다시 서비스계약ID로 정렬.
    # 인덱스 재설정해줌.
    telcom = pd.concat([telcom, df], axis=1)
    del telcom['검증']

    # 서비스계약ID별 상품갯수 추가
    grouped = telcom['서비스계약ID'].groupby(telcom['서비스번호(TRIM)'])

    count = grouped.count().reset_index(name="상품갯수")

    telcom = pd.merge(telcom, count)

    # 서비스번호별 상품갯수 추가

    def func(row):
        if row['청구일자'] >= date_max:
            return 0
        else:
            return 1

    telcom['이탈여부'] = telcom.apply(func, axis=1)
    # 마지막 데이터의 청구일 기준 가장 큰 숫자 시작하지않으면 이탈했다 간주. 이탈여부 1로 표시.

    # 이탈한 달 특성 추가(머신러닝돌릴때는 사용하지않고 분석시에 사용할 것)
    telcom['청구일자'] = telcom['청구일자'].astype(str)

    def func(row):
        if row['이탈여부'] == 1:
            if row['청구일자'][4] == '0':
                return row['청구일자'][5]
            else:
                return row['청구일자'][4:6]
        else:
            return 0

    telcom['이탈한달'] = telcom.apply(func, axis=1)

    # 유지기간
    telcom['개통일(준공일)'] = telcom['개통일(준공일)'].astype(str)
    telcom['개통일(준공일)'] = pd.to_datetime(telcom['개통일(준공일)'])
    telcom['개통일(준공일)'] = telcom['개통일(준공일)'].dt.tz_localize('UTC')

    telcom['청구일자'] = telcom['청구일자'].astype(str)
    telcom['청구일자'] = pd.to_datetime(telcom['청구일자'])
    telcom['청구일자'] = telcom['청구일자'].dt.tz_localize('UTC')

    telcom['유지기간'] = telcom['청구일자'] - telcom['개통일(준공일)']

    # 둘다 int이므로 차를 이용해 날짜를 계산하기 위해 데이터타입 날짜로 변경.
    # 유지기간 행 새로만듦.

    telcom['유지기간'] = telcom['유지기간'].astype(str)

    telcom['유지기간'] = telcom['유지기간'].str.split(n=1, expand=True)

    telcom['유지기간'] = telcom['유지기간'].astype(int)

    # 유지기간을 int 값으로 변경하기 위해
    # 먼저 string으로 변경한 뒤, 뒤에붙은 days를 떼고 int로 변환시킨다.

    telcom['서비스번호(TRIM)'] = telcom['서비스번호(TRIM)'].astype(str)

    # 서비스계약ID U와 N으로 특성추가
    def func(row):
        if row['서비스번호(TRIM)'][0] == 'U':
            return 1  # U이면 1
        else:
            return 0  # N이면 0

    telcom['U/N'] = telcom.apply(func, axis=1)

    # 원핫 인코딩
    def dummy_data(data, columns):
        for column in columns:
            data = pd.concat([data, pd.get_dummies(data[column], prefix=column)], axis=1)
            data = data.drop(column, axis=1)
        return data

    dummy_columns = ['요금항목명', '모상품명', '영업본부명']
    telcom = dummy_data(telcom, dummy_columns)

    del telcom['개통일(준공일)']
    del telcom['해지일']
    del telcom['청구일자']
    del telcom['금액']
    del telcom['할인금액']
    del telcom['계약자명(가입자명)']
    del telcom['서비스번호(TRIM)']
    del telcom['할인율']

    # 그리드서치를위한
    features = ['평균금액', '평균할인율', '상품갯수', '유지기간', 'U/N',
                '요금항목명_관제서비스료', '요금항목명_유지보수료', '요금항목명_임대이용료', '모상품명_CCTV장비',
                '모상품명_IP-PBX장비', '모상품명_그린PC', '모상품명_네트워크관리(고급형)', '모상품명_네트워크관리(기본형)',
                '모상품명_네트워크관리(표준형)', '모상품명_네트워크장비', '모상품명_네트워크장비유지보수', '모상품명_무선랜장비',
                '모상품명_보안관리', '모상품명_보안장비', '모상품명_서버장비', '영업본부명_강북고객본부', '영업본부명_강원고객본부',
                '영업본부명_공공고객본부', '영업본부명_기업고객본부', '영업본부명_대구고객본부', '영업본부명_부산고객본부',
                '영업본부명_수도권강남고객본부', '영업본부명_수도권강북고객본부', '영업본부명_수도권서부고객본부', '영업본부명_전남고객본부',
                '영업본부명_전북고객본부', '영업본부명_제주고객본부', '영업본부명_충남고객본부', '영업본부명_충북고객본부']

    label = '이탈여부'


    import joblib

    model = joblib.load('model/XGB2.pkl')
    telcom['이탈여부'] = model.predict(telcom[features].values)

    telcom.to_excel("_media/Predict_output.xlsx")


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            ml()
            return HttpResponseRedirect('../../analysis')
    else:
        form = UploadFileForm()
    return render(
        request, 'blog/upload.html', {'form': form}
    )


class PostUpdate(UpdateView):
    model = Post
    fields = [
        'title', 'content', 'head_image', 'category',
    ]


class PostListByCategory(ListView):

    def get_queryset(self):
        slug = self.kwargs['slug']

        if slug == '_none':
            category = None
        else:
            category = Category.objects.get(slug=slug)

        return Post.objects.filter(category=category).order_by('-created')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(type(self), self).get_context_data(**kwargs)
        context['category_list'] = Category.objects.all()
        context['posts_without_category'] = Post.objects.filter(category=None).count()

        slug = self.kwargs['slug']

        if slug == '_none':
            context['category'] = '미분류'
        else:
            category = Category.objects.get(slug=slug)
            context['category'] = category

        # context['title'] = 'Blog - {}'.format(category.name)
        return context
