<script setup lang="ts">
import GameView from "./views/GameView.vue";
</script>

<template>
  <GameView />
</template>

<style>
.map-node.assigned .order-tag {
  fill: #71808a;
}

.map-node.assigned circle:not(.pulse) {
  fill: #283640;
  stroke: #65757f;
}

.contract-row {
  display: block;
  width: 100%;
  margin: 8px 0;
  text-align: left;
}

.rover-card .cancel-delivery {
  display: block;
  width: 100%;
  margin-top: 10px;
  padding: 7px 10px;
  border: 1px solid #9a5960;
  background: #2f1e26;
  color: #efb5b8;
  font:
    9px "DM Mono",
    monospace;
  letter-spacing: 0.08em;
  text-align: center;
}

.rover-card {
  position: relative;
  height: 128px;
}

.rover-card footer {
  margin-bottom: 27px;
}

.rover-card .cancel-delivery {
  position: absolute;
  right: 12px;
  bottom: 10px;
  left: 12px;
  width: auto;
}

.rover-card .cancel-delivery:hover {
  border-color: #e58f96;
  background: #48242d;
  color: #fff0f1;
}

.info-panel .point-contract {
  display: grid;
  grid-template-columns: 1fr;
  gap: 6px;
  padding: 12px 0;
}

.info-panel .point-contract dt {
  color: #b8d0dd;
}

.info-panel .contract-details {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: #d9e7ee;
}

.info-panel .point-contract .quiet-button {
  width: 100%;
  padding: 7px;
  border-color: #9a5960;
  color: #efb5b8;
  font-size: 9px;
}
</style>
