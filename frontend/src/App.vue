<template>
  <div class="app-page">
    <div class="aurora-orb aurora-orb-one" aria-hidden="true"></div>
    <div class="aurora-orb aurora-orb-two" aria-hidden="true"></div>

    <div class="app-wrapper">
      <Sidebar :theme="theme" @toggle-theme="toggleTheme" />

      <main class="main-content">
        <DocumentSettings v-if="chatStore.activeNav === 'settings'" />
        <HistorySidebar />
        <ChatArea v-show="chatStore.activeNav !== 'settings'" />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import HistorySidebar from '@/components/HistorySidebar.vue';
import ChatArea from '@/components/Chat/ChatArea.vue';
import DocumentSettings from '@/components/Documents/DocumentSettings.vue';

import { useChatStore } from '@/stores/chat';

const chatStore = useChatStore();

type Theme = 'dark' | 'light';

const storedTheme = localStorage.getItem('supermew-theme');
const theme = ref<Theme>(storedTheme === 'light' ? 'light' : 'dark');

const applyTheme = (nextTheme: Theme) => {
  document.documentElement.dataset.theme = nextTheme;
  document.documentElement.style.colorScheme = nextTheme;
  localStorage.setItem('supermew-theme', nextTheme);
};

const toggleTheme = () => {
  theme.value = theme.value === 'dark' ? 'light' : 'dark';
};

watch(theme, applyTheme, { immediate: true });

</script>
