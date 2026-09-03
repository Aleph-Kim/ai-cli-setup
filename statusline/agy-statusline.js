#!/usr/bin/env node

/**
 * Antigravity CLI Custom Statusline Script
 * Format: {모델명} | {현재 사용량}% current (reset {초기화 시각}) | {주간 사용량}% week (reset {요일|초기화 시각}) | {모드}
 * Example: Gemini 3.8 Flash (High) | 63% current (reset 15:26) | 40% week (reset 일요일|14:33) | Default
 */

const fs = require('fs');

function formatTime(val) {
  if (!val) return 'N/A';

  const date = new Date(val);
  if (isNaN(date.getTime())) return 'N/A';

  // 로컬 시간대 기준 HH:MM 변환
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
}

function formatWeeklyResetTime(val) {
  if (!val) return 'N/A';

  const date = new Date(val);
  if (isNaN(date.getTime())) return 'N/A';

  // 로컬 시간대 기준 요일|HH:MM 변환
  const days = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
  const dayName = days[date.getDay()];
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${dayName}|${hours}:${minutes}`;
}

function calculateUsage(fraction) {
  if (typeof fraction !== 'number') return null;
  const used = (1 - fraction) * 100;
  return Math.max(0, Math.min(100, Math.round(used)));
}

function main() {
  let input = '';
  try {
    input = fs.readFileSync(0, 'utf-8');
  } catch (e) {
    // stdin 읽기 실패
  }

  let data = {};
  if (input && input.trim()) {
    try {
      data = JSON.parse(input);
    } catch (e) {
      process.stdout.write('JSON Parse Error');
      return;
    }
  }

  // 1. 모델명 추출 (display_name에 이미 풀네임이 포함됨)
  let modelName = 'Gemini';
  if (data.model) {
    if (typeof data.model === 'string') {
      modelName = data.model;
    } else {
      modelName = data.model.display_name || data.model.id || 'Gemini';
    }
  }

  // 2. Quota 추출 (현재 모델에 맞춰 gemini 또는 3p 키 동적 매핑)
  const quota = data.quota || {};
  const is3P = modelName.toLowerCase().includes('claude') || 
               modelName.toLowerCase().includes('gpt') || 
               Boolean(quota['3p-5h'] && !quota['gemini-5h']);

  const currentQuotaKey = is3P ? '3p-5h' : 'gemini-5h';
  const weeklyQuotaKey = is3P ? '3p-weekly' : 'gemini-weekly';

  const currentObj = quota[currentQuotaKey] || quota['gemini-5h'] || quota['3p-5h'];
  const weeklyObj = quota[weeklyQuotaKey] || quota['gemini-weekly'] || quota['3p-weekly'];

  // 3. 현재 5시간 사용량 및 리셋 시각 계산
  let currentUsage = null;
  let resetTime = 'N/A';

  if (currentObj) {
    currentUsage = calculateUsage(currentObj.remaining_fraction);
    if (currentObj.reset_time) {
      resetTime = formatTime(currentObj.reset_time);
    }
  }

  // 4. 주간 사용량 및 주간 리셋 정보 계산
  let weekUsage = null;
  let weekResetTime = 'N/A';

  if (weeklyObj) {
    weekUsage = calculateUsage(weeklyObj.remaining_fraction);
    if (weeklyObj.reset_time) {
      weekResetTime = formatWeeklyResetTime(weeklyObj.reset_time);
    }
  }

  // 5. 모드 추출 (미지정 시 Default)
  const mode = data.cycle_mode || 'Default';

  // 6. 최종 문자열 출력
  const displayCurrent = currentUsage !== null ? `${currentUsage}%` : '-';
  const displayWeek = weekUsage !== null ? `${weekUsage}%` : '-';

  const output = `${modelName} | ${displayCurrent} current (reset ${resetTime}) | ${displayWeek} week (reset ${weekResetTime}) | ${mode}`;
  process.stdout.write(output);
}

main();
