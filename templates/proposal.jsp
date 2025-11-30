<!DOCTYPE html>
<html lang="ko" class="scroll-smooth">

<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="ITGC 전문 인력 부재와 수동 관리의 비효율성을 동시에 해결하는 Snowball 솔루션">
  <title>Snowball - 내부통제 솔루션</title>
  <link rel="icon" type="image/x-icon" href="/static/proposal/img/favicon.ico">
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
    rel="stylesheet">
  <link rel="stylesheet" href="/static/proposal/style.css">
</head>

<body class="antialiased text-slate-800 bg-slate-50">

  <nav class="bg-white/90 backdrop-blur-md shadow-sm fixed w-full top-0 z-50 transition-all duration-300">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-20">
        <div class="flex-shrink-0">
          <a href="#" class="flex items-center text-2xl font-bold text-[#2c5265] tracking-tight">
            <img src="/static/proposal/img/favicon.ico" alt="Snowball Logo" class="w-8 h-8 mr-3">
            Snowball
          </a>
        </div>

        <div class="hidden md:flex space-x-8 items-center">
          <a href="#home" class="text-slate-600 hover:text-[#2c5265] font-medium transition-colors">Home</a>
          <a href="#track-a" class="text-slate-600 hover:text-[#2c5265] font-medium transition-colors">Track A</a>
          <a href="#track-b" class="text-slate-600 hover:text-[#2c5265] font-medium transition-colors">Track B</a>
          <a href="#benefits" class="text-slate-600 hover:text-[#2c5265] font-medium transition-colors">Benefits</a>
          <a href="#contact"
            class="px-5 py-2.5 bg-[#2c5265] text-white rounded-full font-medium hover:bg-[#1a3c4d] transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5">Contact</a>
        </div>

        <div class="md:hidden">
          <button id="mobile-menu-button" class="text-slate-600 hover:text-[#2c5265] focus:outline-none p-2">
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <div id="mobile-menu" class="hidden md:hidden bg-white border-t border-gray-100 shadow-lg absolute w-full">
      <div class="px-4 pt-2 pb-4 space-y-1">
        <a href="#home"
          class="block px-3 py-3 text-slate-600 hover:bg-slate-50 hover:text-[#2c5265] rounded-lg font-medium">Home</a>
        <a href="#track-a"
          class="block px-3 py-3 text-slate-600 hover:bg-slate-50 hover:text-[#2c5265] rounded-lg font-medium">Track A -
          PA 서비스</a>
        <a href="#track-b"
          class="block px-3 py-3 text-slate-600 hover:bg-slate-50 hover:text-[#2c5265] rounded-lg font-medium">Track B -
          Snowball 시스템</a>
        <a href="#benefits"
          class="block px-3 py-3 text-slate-600 hover:bg-slate-50 hover:text-[#2c5265] rounded-lg font-medium">Benefits</a>
        <a href="#contact" class="block px-3 py-3 text-[#2c5265] font-bold hover:bg-slate-50 rounded-lg">Contact</a>
      </div>
    </div>
  </nav>

  <section id="home"
    class="pt-24 pb-16 md:pt-32 md:pb-24 bg-gradient-to-br from-[#2c5265] via-[#234557] to-[#152a38] text-white relative overflow-hidden">
    <!-- Decorative elements -->
    <div class="absolute top-0 left-0 w-full h-full overflow-hidden opacity-10 pointer-events-none">
      <div class="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-white blur-3xl"></div>
      <div class="absolute bottom-0 right-0 w-[500px] h-[500px] rounded-full bg-blue-400 blur-3xl"></div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
      <span
        class="inline-block py-1 px-3 rounded-full bg-white/10 border border-white/20 text-sm font-medium mb-6 backdrop-blur-sm">
        Internal Control Solution
      </span>
      <h1 class="text-3xl md:text-5xl lg:text-6xl font-extrabold mb-6 md:mb-8 leading-tight tracking-tight">
        복잡한 내부통제,<br />
        <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-200 to-white">Snowball</span>과 함께 해결하세요
      </h1>

      <p class="text-lg md:text-xl lg:text-2xl mb-10 md:mb-12 text-slate-200 max-w-3xl mx-auto font-light leading-relaxed">
        IT 전문 인력 부재와 수동 관리의 비효율성.<br />
        Snowball은 이 두 가지 난관을 동시에 해결하는 최적의 파트너입니다.
      </p>

      <div class="flex flex-col sm:flex-row gap-4 justify-center mt-6 md:mt-8">
        <a href="#track-a"
          class="px-6 py-3.5 md:px-8 md:py-4 bg-white text-[#2c5265] font-bold rounded-xl shadow-xl hover:shadow-2xl hover:bg-blue-50 transition-all transform hover:-translate-y-1 text-center">
          Track A (서비스) 보기
        </a>
        <a href="#track-b"
          class="px-6 py-3.5 md:px-8 md:py-4 bg-white/10 backdrop-blur-md border border-white/30 text-white font-bold rounded-xl hover:bg-white/20 transition-all transform hover:-translate-y-1 text-center">
          Track B (시스템) 보기
        </a>
      </div>

      <div class="mt-16 animate-bounce text-white/50">
        <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
        </svg>
      </div>
    </div>
  </section>

  <section class="py-16 md:py-24 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-10 md:mb-16">
        <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold text-slate-900 mb-3 md:mb-4">
          현재 내부통제 운영의 <span class="text-red-500">Pain Point</span>
        </h2>
        <p class="text-base md:text-lg text-slate-600 max-w-2xl mx-auto px-4">
          많은 기업들이 겪고 있는 내부통제 운영의 현실적인 어려움들입니다.
        </p>
      </div>

      <div class="grid md:grid-cols-2 gap-6 md:gap-8 max-w-5xl mx-auto">
        <div
          class="group bg-slate-50 rounded-2xl p-6 md:p-8 border border-slate-100 hover:border-blue-200 hover:shadow-xl transition-all duration-300">
          <div
            class="w-14 h-14 md:w-16 md:h-16 bg-blue-100 rounded-2xl flex items-center justify-center text-2xl md:text-3xl mb-5 md:mb-6 group-hover:scale-110 transition-transform duration-300">
            👤</div>
          <h3 class="text-xl md:text-2xl font-bold mb-3 md:mb-4 text-slate-900">IT 전문 인력 부재</h3>
          <p class="text-slate-600 leading-relaxed text-base md:text-lg">
            내부통제팀 내 ITGC 전담 전문가를 채용하고 유지하는 데 어려움이 있으며, 높은 인건비와 이직률로 인한 업무 공백이 발생합니다.
          </p>
        </div>

        <div
          class="group bg-slate-50 rounded-2xl p-6 md:p-8 border border-slate-100 hover:border-blue-200 hover:shadow-xl transition-all duration-300">
          <div
            class="w-14 h-14 md:w-16 md:h-16 bg-red-100 rounded-2xl flex items-center justify-center text-2xl md:text-3xl mb-5 md:mb-6 group-hover:scale-110 transition-transform duration-300">
            ⏰</div>
          <h3 class="text-xl md:text-2xl font-bold mb-3 md:mb-4 text-slate-900">비효율적 수동 관리</h3>
          <p class="text-slate-600 leading-relaxed text-base md:text-lg">
            엑셀 기반의 수동 관리와 문서 취합 과정에서 버전 관리 오류가 빈발하며, 단순 반복 업무로 인해 핵심 리스크 관리에 집중하기 어렵습니다.
          </p>
        </div>
      </div>
    </div>
  </section>

  <section class="py-16 md:py-24 bg-[#2c5265] text-white relative overflow-hidden">
    <!-- Background Pattern -->
    <div
      class="absolute inset-0 opacity-10 bg-[radial-gradient(#ffffff_1px,transparent_1px)] [background-size:20px_20px]">
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
      <div class="text-center mb-10 md:mb-16 px-4">
        <span
          class="inline-block py-1 px-3 rounded-full bg-white/10 border border-white/20 text-xs md:text-sm font-medium mb-4 md:mb-6 backdrop-blur-sm text-blue-200">
          Why Snowball?
        </span>
        <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold mb-4 md:mb-6">
          왜 <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-200 to-white">Snowball</span>이어야 할까요?
        </h2>
        <p class="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto font-light">
          PA 서비스만 제공하거나 시스템만 구축하는 회사는 많습니다.<br />
          하지만 Snowball은 다릅니다.
        </p>
      </div>

      <div class="grid md:grid-cols-2 gap-6 lg:gap-12">
        <!-- Feature 1: Hybrid Solution -->
        <div
          class="bg-white/5 backdrop-blur-lg rounded-2xl md:rounded-3xl p-5 md:p-8 border border-white/10 hover:bg-white/10 transition-all duration-300 group">
          <div class="flex items-start gap-4 md:gap-6">
            <div
              class="w-12 h-12 md:w-16 md:h-16 rounded-xl md:rounded-2xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center text-2xl md:text-3xl shadow-lg group-hover:scale-110 transition-transform duration-300 shrink-0">
              💎
            </div>
            <div>
              <h3 class="text-xl md:text-2xl font-bold mb-2 md:mb-3 text-white">유일무이한 하이브리드 솔루션</h3>
              <p class="text-slate-300 leading-relaxed mb-3 md:mb-4 text-sm md:text-base">
                "시스템 따로, 인력 따로?"<br />
                Snowball은 <span class="text-white font-bold">PA 서비스(인력)</span>와 <span
                  class="text-white font-bold">시스템(솔루션)</span>을 완벽하게 결합하여 제공하는 유일한 파트너입니다.
              </p>
              <ul class="space-y-1.5 md:space-y-2 text-xs md:text-sm text-slate-400">
                <li class="flex items-center"><span class="text-blue-400 mr-2">✓</span>시스템 구축과 운영 인력 동시 해결</li>
                <li class="flex items-center"><span class="text-blue-400 mr-2">✓</span>단절 없는 원스톱 내부통제 관리</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Feature 2: Expert Background -->
        <div
          class="bg-white/5 backdrop-blur-lg rounded-2xl md:rounded-3xl p-5 md:p-8 border border-white/10 hover:bg-white/10 transition-all duration-300 group">
          <div class="flex items-start gap-4 md:gap-6">
            <div
              class="w-12 h-12 md:w-16 md:h-16 rounded-xl md:rounded-2xl bg-gradient-to-br from-emerald-500 to-green-400 flex items-center justify-center text-2xl md:text-3xl shadow-lg group-hover:scale-110 transition-transform duration-300 shrink-0">
              🎓
            </div>
            <div>
              <h3 class="text-xl md:text-2xl font-bold mb-2 md:mb-3 text-white">검증된 전문가 그룹</h3>
              <p class="text-slate-300 leading-relaxed mb-3 md:mb-4 text-sm md:text-base">
                이론과 현장을 모두 경험한 전문가가 만났습니다.<br />
                <span class="text-white font-bold">대기업 IT 현장과 Big 4 회계법인을 모두 경험한 전문가</span>가 직접 설계하고 서비스합니다.
              </p>
              <ul class="space-y-1.5 md:space-y-2 text-xs md:text-sm text-slate-400">
                <li class="flex items-center"><span class="text-emerald-400 mr-2">✓</span>IT 실무와 회계 감사의 완벽한 이해</li>
                <li class="flex items-center"><span class="text-emerald-400 mr-2">✓</span>감사인 관점의 선제적 이슈 대응</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="py-16 md:py-24 bg-slate-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-12 md:mb-16">
        <span class="text-[#2c5265] font-semibold tracking-wider uppercase text-sm">Our Solutions</span>
        <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold text-slate-900 mt-2">
          Snowball의 두 가지 솔루션
        </h2>
      </div>

      <div id="track-a" class="scroll-mt-24 mb-20">
        <div class="bg-white rounded-3xl overflow-hidden shadow-2xl border border-slate-100">
          <div
            class="bg-[#2c5265] p-6 md:p-10 text-white flex flex-col md:flex-row items-start md:items-center justify-between">
            <div>
              <div class="flex items-center gap-4 mb-2">
                <span class="bg-white/20 backdrop-blur px-4 py-1.5 rounded-lg font-bold text-sm">Track A</span>
                <h3 class="text-2xl md:text-3xl font-bold">PA 서비스</h3>
              </div>
              <p class="text-blue-100 text-lg max-w-2xl">
                IT 전담 인원이 내부통제팀 직원과 동일하게 업무 전 과정을 상시 수행합니다.
              </p>
            </div>
            <div class="mt-6 md:mt-0">
              <span class="text-5xl opacity-20">🤝</span>
            </div>
          </div>

          <div class="p-6 md:p-12">
            <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div class="space-y-4">
                <div
                  class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-[#2c5265] font-bold text-xl">
                  1</div>
                <h4 class="font-bold text-lg text-slate-900">RCM 설계 및 표준화</h4>
                <ul class="text-slate-600 space-y-2 text-sm">
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>ITGC RCM 최신화/표준화</li>
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>설계평가 수행</li>
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>통제 매뉴얼 작성 지원</li>
                </ul>
              </div>

              <div class="space-y-4">
                <div
                  class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-[#2c5265] font-bold text-xl">
                  2</div>
                <h4 class="font-bold text-lg text-slate-900">운영평가 대행</h4>
                <ul class="text-slate-600 space-y-2 text-sm">
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>평가 계획 및 샘플링</li>
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>증적 취합 및 검증</li>
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>결함 발견 및 분석</li>
                </ul>
              </div>

              <div class="space-y-4">
                <div
                  class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-[#2c5265] font-bold text-xl">
                  3</div>
                <h4 class="font-bold text-lg text-slate-900">보고서 및 조서 산출</h4>
                <ul class="text-slate-600 space-y-2 text-sm">
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>표준화된 평가 조서 작성</li>
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>결함 시정 조치 보고</li>
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>내부 보고서 작성</li>
                </ul>
              </div>

              <div class="space-y-4">
                <div
                  class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center text-[#2c5265] font-bold text-xl">
                  4</div>
                <h4 class="font-bold text-lg text-slate-900">감사 대응 지원</h4>
                <ul class="text-slate-600 space-y-2 text-sm">
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>외부 감사 자료 준비</li>
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>감사인 질의 대응</li>
                  <li class="flex items-start"><span class="mr-2 text-blue-500">•</span>감사 조서 검토 및 보완</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div id="track-b" class="scroll-mt-24">
        <div class="bg-white rounded-3xl overflow-hidden shadow-2xl border border-slate-100">
          <div
            class="bg-gradient-to-r from-emerald-600 to-teal-600 p-6 md:p-10 text-white flex flex-col md:flex-row items-start md:items-center justify-between">
            <div>
              <div class="flex items-center gap-4 mb-2">
                <span class="bg-white/20 backdrop-blur px-4 py-1.5 rounded-lg font-bold text-sm">Track B</span>
                <h3 class="text-2xl md:text-3xl font-bold">Snowball 시스템</h3>
              </div>
              <p class="text-emerald-50 text-lg max-w-2xl">
                내부통제 전 영역(ELC, TLC, ITGC)을 하나의 플랫폼에서 통합 관리하는 솔루션입니다.
              </p>
            </div>
            <div class="mt-6 md:mt-0">
              <span class="text-5xl opacity-20">💻</span>
            </div>
          </div>

          <div class="p-6 md:p-12">
            <div class="grid md:grid-cols-2 gap-8 mb-12">
              <div class="bg-emerald-50/50 rounded-2xl p-6 border border-emerald-100">
                <h4 class="font-bold text-xl mb-3 text-emerald-700 flex items-center">
                  <span class="mr-2">☁️</span> Cloud (구독형, SaaS)
                </h4>
                <ul class="text-slate-700 space-y-2 text-base pl-2">
                  <li class="flex items-center"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-2"></span>초기 투자
                    부담 최소화 (경제성)</li>
                  <li class="flex items-center"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-2"></span>인프라 구축
                    없이 즉시 운영 (신속성)</li>
                  <li class="flex items-center"><span class="w-1.5 h-1.5 bg-emerald-500 rounded-full mr-2"></span>기능
                    업데이트 자동 적용</li>
                </ul>
              </div>

              <div class="bg-slate-50 rounded-2xl p-6 border border-slate-200">
                <h4 class="font-bold text-xl mb-3 text-slate-700 flex items-center">
                  <span class="mr-2">🏢</span> On-Premise (구축형)
                </h4>
                <ul class="text-slate-700 space-y-2 text-base pl-2">
                  <li class="flex items-center"><span class="w-1.5 h-1.5 bg-slate-500 rounded-full mr-2"></span>내부망 운영으로
                    보안 정책 준수</li>
                  <li class="flex items-center"><span class="w-1.5 h-1.5 bg-slate-500 rounded-full mr-2"></span>기존
                    ERP/레거시 시스템 직접 연계</li>
                  <li class="flex items-center"><span class="w-1.5 h-1.5 bg-slate-500 rounded-full mr-2"></span>회사 상황에
                    맞춘 커스터마이징</li>
                </ul>
              </div>
            </div>

            <div class="border-t border-slate-100 pt-10">
              <h4 class="font-bold mb-8 text-slate-900 text-2xl text-center">시스템 주요 기능 미리보기</h4>
              <div class="grid md:grid-cols-2 gap-10">
                <div class="group">
                  <div
                    class="overflow-hidden rounded-xl shadow-lg border border-slate-200 mb-3 md:mb-4 bg-slate-100 aspect-video relative">
                    <img src="/static/proposal/img/dashboard.png" alt="대시보드" loading="lazy"
                      class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500">
                    <div class="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors"></div>
                  </div>
                  <h5 class="font-bold text-base md:text-lg text-slate-800 mb-1.5 md:mb-2">1. 종합 대시보드</h5>
                  <p class="text-slate-600 text-sm leading-relaxed">
                    ELC, TLC, ITGC 평가 결과를 통합 조회하고 종합 리포트를 생성합니다. 회사별/통제 영역별 평가 현황을 한눈에 파악할 수 있습니다.
                  </p>
                </div>

                <div class="group">
                  <div
                    class="overflow-hidden rounded-xl shadow-lg border border-slate-200 mb-3 md:mb-4 bg-slate-100 aspect-video relative">
                    <img src="/static/proposal/img/rcm.png" alt="RCM 관리" loading="lazy"
                      class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500">
                    <div class="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors"></div>
                  </div>
                  <h5 class="font-bold text-base md:text-lg text-slate-800 mb-1.5 md:mb-2">2. RCM 관리</h5>
                  <p class="text-slate-600 text-sm leading-relaxed">
                    위험통제매트릭스(RCM) 데이터를 중앙 관리하며, 엑셀 기반 파일 업로드 및 버전 관리를 지원합니다.
                  </p>
                </div>

                <div class="group">
                  <div
                    class="overflow-hidden rounded-xl shadow-lg border border-slate-200 mb-3 md:mb-4 bg-slate-100 aspect-video relative">
                    <img src="/static/proposal/img/design_test.png" alt="설계 평가" loading="lazy"
                      class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500">
                    <div class="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors"></div>
                  </div>
                  <h5 class="font-bold text-base md:text-lg text-slate-800 mb-1.5 md:mb-2">3. 설계 평가</h5>
                  <p class="text-slate-600 text-sm leading-relaxed">
                    통제활동 설명 검토, 현실 반영도 평가 후 증빙 및 결과를 입력하여 설계 효과성을 종합 판정합니다.
                  </p>
                </div>

                <div class="group">
                  <div
                    class="overflow-hidden rounded-xl shadow-lg border border-slate-200 mb-3 md:mb-4 bg-slate-100 aspect-video relative">
                    <img src="/static/proposal/img/operation_test.png" alt="운영 평가" loading="lazy"
                      class="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500">
                    <div class="absolute inset-0 bg-black/0 group-hover:bg-black/5 transition-colors"></div>
                  </div>
                  <h5 class="font-bold text-base md:text-lg text-slate-800 mb-1.5 md:mb-2">4. 운영 평가</h5>
                  <p class="text-slate-600 text-sm leading-relaxed">
                    테스트 절차 자동 생성, 표본 크기 자동 계산, 표본별 증빙 및 결과 입력 후 전체 결론을 자동 산출합니다.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section id="benefits" class="py-16 md:py-24 bg-white scroll-mt-24">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="text-center mb-10 md:mb-16 px-4">
        <h2 class="text-2xl md:text-3xl lg:text-4xl font-bold text-slate-900 mb-3 md:mb-4">
          Snowball 도입의 실질적 이점
        </h2>
        <p class="text-base md:text-lg text-slate-600">
          비용은 줄이고, 효율과 안정성은 높입니다.
        </p>
      </div>

      <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-5 md:gap-6">
        <div
          class="bg-slate-50 rounded-2xl p-5 md:p-8 hover:bg-white hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-slate-100">
          <div class="text-3xl md:text-4xl mb-4 md:mb-6">🛡️</div>
          <h3 class="text-lg md:text-xl font-bold mb-2 md:mb-3 text-slate-900">감사 대응력 강화</h3>
          <p class="text-slate-600 text-sm leading-relaxed">
            전문가의 감사 이슈 대응 및 지원으로 외부 감사 시 발생하는 질의와 이슈를 신속하게 해결합니다.
          </p>
        </div>

        <div
          class="bg-slate-50 rounded-2xl p-5 md:p-8 hover:bg-white hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-slate-100">
          <div class="text-3xl md:text-4xl mb-4 md:mb-6">🚀</div>
          <h3 class="text-lg md:text-xl font-bold mb-2 md:mb-3 text-slate-900">업무 효율화</h3>
          <p class="text-slate-600 text-sm leading-relaxed">
            반복적 수동 업무를 제거하고 자동화하여, 빠르고 정확한 평가 결과를 도출합니다.
          </p>
        </div>

        <div
          class="bg-slate-50 rounded-2xl p-5 md:p-8 hover:bg-white hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-slate-100">
          <div class="text-3xl md:text-4xl mb-4 md:mb-6">📊</div>
          <h3 class="text-lg md:text-xl font-bold mb-2 md:mb-3 text-slate-900">운영 가시성 확보</h3>
          <p class="text-slate-600 text-sm leading-relaxed">
            실시간 대시보드를 제공하여 ICFR 전 영역의 통제 수행 현황 및 결함 현황을 즉시 파악할 수 있습니다.
          </p>
        </div>

        <div
          class="bg-slate-50 rounded-2xl p-5 md:p-8 hover:bg-white hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-slate-100">
          <div class="text-3xl md:text-4xl mb-4 md:mb-6">🎯</div>
          <h3 class="text-lg md:text-xl font-bold mb-2 md:mb-3 text-slate-900">리스크 관리 강화</h3>
          <p class="text-slate-600 text-sm leading-relaxed">
            체계적인 결함 추적과 시정 조치 관리를 통해 내부통제 역량을 극대화하고 리스크를 최소화합니다.
          </p>
        </div>
      </div>
    </div>
  </section>

  <section class="py-16 md:py-24 bg-[#1a3c4d] text-white relative overflow-hidden">
    <div class="absolute inset-0 bg-[url('img/pattern.png')] opacity-5"></div>
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
      <h2 class="text-xl md:text-3xl lg:text-4xl font-bold mb-6 md:mb-8 leading-tight">
        지금 바로 Snowball의 효과를 경험해보세요
      </h2>

      <p class="text-lg md:text-xl mb-8 md:mb-12 text-slate-300 font-light">
        내부통제 전문가의 1:1 상담을 통해<br />
        귀사의 상황에 맞는 최적의 솔루션을 제안해 드립니다.
      </p>

      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <a href="#contact"
          class="px-8 py-3.5 md:px-10 md:py-4 bg-green-500 text-white font-bold rounded-xl shadow-lg hover:bg-green-600 transition-all transform hover:scale-105">
          상담 신청하기
        </a>
      </div>
    </div>
  </section>

  <footer id="contact" class="bg-slate-900 text-slate-400 py-16 scroll-mt-24 border-t border-slate-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="grid md:grid-cols-2 gap-12">
        <div>
          <div class="flex items-center text-2xl font-bold text-white mb-6">
            <img src="/static/proposal/img/favicon.ico" alt="Snowball Logo" class="w-8 h-8 mr-3 grayscale brightness-200">
            Snowball
          </div>
          <p class="text-slate-500 mb-6 max-w-sm">
            Snowball은 기업의 내부통제(ICFR)를 혁신하는 전문 솔루션 파트너입니다. 복잡한 규제 준수와 비효율적인 업무 프로세스를 한 번에 해결하세요.
          </p>
        </div>

        <div>
          <h4 class="text-lg font-bold text-white mb-6">Contact Us</h4>
          <div class="space-y-4">
            <a href="mailto:snowball1566@gmail.com" class="flex items-center hover:text-white transition-colors group">
              <div
                class="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center mr-4 group-hover:bg-slate-700 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              snowball1566@gmail.com
            </a>
            <a href="http://www.snowball1566.com" target="_blank" rel="noopener noreferrer"
              class="flex items-center hover:text-white transition-colors group">
              <div
                class="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center mr-4 group-hover:bg-slate-700 transition-colors">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 019-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                </svg>
              </div>
              www.snowball1566.com
            </a>
          </div>
        </div>
      </div>

      <div class="border-t border-slate-800 mt-12 pt-8 text-center text-sm text-slate-600">
        <p>&copy; 2025 Snowball. All rights reserved.</p>
      </div>
    </div>
  </footer>

  <script>
    // Mobile menu toggle
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    menuButton?.addEventListener('click', () => {
      mobileMenu?.classList.toggle('hidden');
    });

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          // Close mobile menu after click
          mobileMenu?.classList.add('hidden');
        }
      });
    });
  </script>

</body>

</html>