<script setup lang="ts">
defineProps<{ turn: number; money: number; score: number; busy: boolean }>()
defineEmits<{ nextTurn: [] }>()
</script>

<template>
  <header class="topbar">
    <div class="brand"><span class="brand-mark">◒</span><div><strong>MOON COURIER</strong><small>CRISIS CONTROL</small></div></div>
    <div class="telemetry"><span>TURN <b>{{ turn }}</b></span><span>¢ <b>{{ money }}</b></span><span>✦ <b>{{ score }}</b></span></div>
    <button class="next-turn" :disabled="busy" @click="$emit('nextTurn')">{{ busy ? 'PROCESSING…' : 'NEXT TURN  →' }}</button>
  </header>
</template>
