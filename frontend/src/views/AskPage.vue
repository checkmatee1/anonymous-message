<template>
  <div class="min-h-screen bg-gray-50 flex flex-col items-center py-8 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    
    <div class="w-full max-w-xl flex flex-col md:flex-row gap-12 md:h-[85vh]">
        
        <!-- Left Column: Mailbox & Input Area -->
        <div class="relative flex-1 flex flex-col items-center justify-center perspective-1000 order-1 md:order-none min-h-[80vh] md:min-h-0 md:pt-24">
             <!-- Header (Mobile Only) -->
             <div 
                class="text-center mb-8 md:hidden w-full transition-opacity duration-300"
                :class="{ 'opacity-0 pointer-events-none': isSent }"
             >
                 <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">匿名留言箱</h1>
                 <p class="text-sm text-gray-600">无需登录，留言仅收件人可见</p>
             </div>
             
             <!-- Header (Desktop - above mailbox) -->
             <div class="text-center mb-8 hidden md:block z-10 w-full absolute top-0 left-0 right-0">
                 <h1 class="text-3xl font-extrabold text-gray-900 tracking-tight">匿名留言箱</h1>
                 <p class="text-sm text-gray-600">无需登录，留言仅收件人可见</p>
             </div>
             <!-- Mailbox Container (Background) -->
             <div 
                class="absolute inset-0 flex items-center justify-center transition-all duration-700 ease-in-out"
                :class="{ 
                    'blur-sm scale-90 opacity-80': !isAnimating && !isSent, 
                    'blur-0 scale-110 opacity-100': isAnimating || isSent
                }"
             >
                <!-- Redesigned Mailbox: Modern Rounded Box Style -->
                <div class="relative w-72 h-80 bg-gradient-to-b from-gray-800 to-black rounded-[3rem] shadow-2xl flex flex-col items-center border-t border-white/10">
                     <!-- Lid / Top Section -->
                     <div class="w-full h-32 bg-black/30 rounded-t-[3rem] border-b border-gray-900/50 flex items-center justify-center relative">
                         <!-- Slot -->
                         <div class="w-48 h-4 bg-black/60 rounded-full shadow-[inset_0_2px_4px_rgba(0,0,0,0.8)] border-b border-white/10"></div>
                     </div>
                     
                     <!-- Body Section -->
                     <div class="flex-1 w-full flex flex-col items-center justify-center relative">
                         <!-- Label -->
                         <div class="font-black text-gray-200/80 tracking-[0.5em] text-2xl">MAIL</div>
                         <div class="text-gray-400/50 text-[10px] tracking-widest mt-1">QA BOX</div>
                         
                         <!-- Decorative Lines -->
                         <div class="absolute bottom-8 w-12 h-1 bg-gray-700/40 rounded-full"></div>
                         <div class="absolute bottom-6 w-8 h-1 bg-gray-700/40 rounded-full"></div>
                     </div>

                     <!-- Success State (INSIDE Mailbox) -->
                     <div v-if="isSent && !isAnimating" class="absolute inset-0 z-30 flex flex-col items-center justify-center p-6 text-center animate-fade-in-up bg-white/95 backdrop-blur-sm rounded-[3rem] overflow-hidden">
                         <div class="flex items-center justify-center h-10 w-10 rounded-full bg-green-100 mb-3 shadow-inner shrink-0">
                            <svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
                         </div>
                         <h3 class="text-lg font-bold text-gray-900 mb-1">投递成功!</h3>
                         <p class="text-xs text-gray-500 mb-4">留言已送达，仅收件人可见。</p>
                         
                         <div class="space-y-2 w-full px-2">
                             <button @click="resetForm" class="w-full py-2 px-4 bg-gray-900 hover:bg-black text-white rounded-lg shadow transition-colors font-medium text-xs">
                                再写一封
                             </button>
                             <button v-if="canRevoke" @click="revokeQuestion" class="w-full py-2 px-4 bg-gray-50 hover:bg-gray-100 text-gray-700 border border-gray-200 rounded-lg transition-colors text-xs">
                                撤回
                             </button>
                         </div>
                     </div>
                </div>
             </div>

             <!-- Envelope / Input Form -->
             <div 
                class="w-full max-w-md bg-white rounded-xl shadow-2xl p-8 relative z-20 transition-all duration-700 ease-in-out transform"
                :class="{ 
                    'translate-y-[200px] -translate-z-[200px] scale-50 opacity-0': isAnimating,
                    'opacity-100': !isSent && !isAnimating,
                    'hidden': isSent && !isAnimating
                }"
             >
                <div class="absolute -top-3 -right-3 w-12 h-12 bg-red-500 rounded-full flex items-center justify-center shadow-lg transform rotate-12">
                    <span class="text-white font-bold text-xs">NEW</span>
                </div>

                <div class="mb-6 border-b-2 border-dashed border-gray-200 pb-4">
                    <h2 class="text-2xl font-serif text-gray-800 font-bold md:block hidden">给我留个言</h2>
                    <div class="flex justify-between items-center text-sm text-gray-500 mt-1">
                        <label class="flex items-center gap-2 min-w-0">
                            <span>From:</span>
                            <input v-model="senderName" maxlength="40" placeholder="匿名朋友" aria-label="称呼（选填，不填就是匿名）" autocomplete="off" class="min-w-0 w-32 bg-transparent border-b border-gray-200 py-1 outline-none focus:border-gray-600 placeholder:text-gray-500" />
                        </label>
                        <span class="font-mono">{{ new Date().toLocaleDateString() }}</span>
                    </div>
                </div>
                
                <textarea 
                    v-model="questionContent"
                    maxlength="5000"
                    class="w-full h-40 resize-none outline-none text-gray-700 bg-gray-50/50 p-4 rounded-lg placeholder-gray-400 focus:bg-gray-100 focus:ring-2 focus:ring-gray-300 transition-all"
                    placeholder="想说什么都可以，只有我能看到。"
                ></textarea>
                
                <button 
                    @click="triggerSendAnimation"
                    :disabled="!canSend"
                    class="mt-8 w-full bg-gray-900 hover:bg-black text-white font-bold py-4 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                    <span class="tracking-widest uppercase text-sm">投递信件</span>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                </button>
             </div>
        </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { questionApi } from '@/api'
const questionContent = ref('')
const senderName = ref('')
const isAnimating = ref(false)
const isSent = ref(false)
const canRevoke = ref(false)
const lastToken = ref('')
const canSend = computed(() => questionContent.value.trim().length > 0 && !isAnimating.value)
const triggerSendAnimation = async () => {
  if (!canSend.value) return
  isAnimating.value = true
  try {
    const { data } = await questionApi.submitQuestion({ content: questionContent.value.trim(), sender_name: senderName.value.trim() || null, images: [] })
    lastToken.value = data.access_token
    canRevoke.value = true
    isSent.value = true
  } catch (error) {
    alert(error.response?.status === 429 ? '投递太频繁，请稍后再试。' : '发送失败，请稍后重试。')
  } finally {
    isAnimating.value = false
  }
}
const resetForm = () => {
  isSent.value = false
  questionContent.value = ''
  senderName.value = ''
  canRevoke.value = false
  lastToken.value = ''
}
const revokeQuestion = async () => {
  if (!lastToken.value || !confirm('确定撤回刚才的留言？')) return
  try {
    await questionApi.revokeQuestion(lastToken.value)
    resetForm()
  } catch {
    alert('撤回失败，留言可能已被处理。')
  }
}
</script>

<style scoped>
.perspective-1000 {
    perspective: 1000px;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translate3d(0, 20px, 0);
    }
    to {
        opacity: 1;
        transform: translate3d(0, 0, 0);
    }
}

.animate-fade-in-up {
    animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Custom scrollbar for list area */
.custom-scrollbar::-webkit-scrollbar {
    width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
    background-color: rgba(156, 163, 175, 0.3);
    border-radius: 20px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background-color: rgba(156, 163, 175, 0.5);
}
</style>
