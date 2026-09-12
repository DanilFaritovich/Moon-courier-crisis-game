<script setup lang="ts">
import type { MapPoint, Order, Rover } from "../../types/game";
defineProps<{
  rover: Rover;
  order: Order;
  destination?: MapPoint;
  batteryAfter?: number;
  busy: boolean;
}>();
defineEmits<{ confirm: []; close: [] }>();
</script>
<template>
  <div class="dialog-backdrop">
    <section
      class="delivery-dialog"
      role="dialog"
      aria-modal="true"
      aria-labelledby="delivery-title"
    >
      <span class="eyebrow">CONFIRM DEPLOYMENT</span>
      <h2 id="delivery-title">Assign {{ rover.name }}</h2>
      <p>
        Send rover {{ rover.name }} to
        <b>{{ destination?.name ?? `point ${order.destination_point_id}` }}</b>
        for contract #{{ order.id }}.
      </p>
      <dl>
        <div>
          <dt>PAYLOAD</dt>
          <dd>{{ order.weight }} kg</dd>
        </div>
        <div>
          <dt>REWARD</dt>
          <dd>¢{{ order.reward }}</dd>
        </div>
        <div>
          <dt>BATTERY</dt>
          <dd>{{ rover.battery }}% → {{ batteryAfter ?? "—" }}%</dd>
        </div>
      </dl>
      <footer>
        <button class="quiet-button" :disabled="busy" @click="$emit('close')">
          CANCEL</button
        ><button
          class="confirm-button"
          data-testid="confirm-delivery"
          :disabled="busy"
          @click="$emit('confirm')"
        >
          {{ busy ? "ASSIGNING…" : "CONFIRM DELIVERY" }}
        </button>
      </footer>
    </section>
  </div>
</template>
