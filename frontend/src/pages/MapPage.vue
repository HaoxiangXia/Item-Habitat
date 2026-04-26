<template>
  <div class="map-page">
    <PageHeader title="地图" subtitle="每张照片都是一个栖息地的记忆">
      <template #actions>
        <Button @click="showAddModal = true" class="add-space-btn">
          <template #icon>
            <plus-icon size="18" />
          </template>
          添加新空间
        </Button>
      </template>
    </PageHeader>
    
    <div class="photo-wall-container">
      <div class="whiteboard">
        <!-- 装饰性白板笔 -->
        <div class="marker marker-blue"></div>
        <div class="marker marker-red"></div>
        
        <div class="photo-wall">
          <div 
            v-for="(photo, index) in photos" 
            :key="index"
            class="polaroid-wrapper"
            :style="getPolaroidStyle(index)"
          >
            <div class="polaroid">
              <div class="photo-container">
                <img :src="photo.url" :alt="photo.note" />
              </div>
              <div class="polaroid-caption">
                <span class="handwritten">{{ photo.note }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加新空间弹窗 -->
    <Modal :open="showAddModal" title="添加新空间" @close="showAddModal = false">
      <div class="add-space-form">
        <div class="form-group">
          <label>空间名称</label>
          <Input v-model="newSpace.name" placeholder="例如：我的书桌" />
        </div>
        <div class="form-group">
          <label>上传实拍照</label>
          <div class="upload-placeholder">
            <div class="upload-icon">📸</div>
            <p>点击或拖拽照片至此</p>
          </div>
        </div>
        <div class="form-group">
          <label>手写备注</label>
          <Textarea v-model="newSpace.note" placeholder="写下对这个空间的记忆..." />
        </div>
        <div class="form-actions">
          <Button variant="secondary" @click="showAddModal = false">取消</Button>
          <Button @click="handleAddSpace">确认添加</Button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script>
import { ref } from 'vue'
import PageHeader from '../components/layout/PageHeader.vue'
import Button from '../components/ui/Button.vue'
import Modal from '../components/ui/Modal.vue'
import Input from '../components/ui/Input.vue'
import Textarea from '../components/ui/Textarea.vue'
import { PlusIcon } from '../components/icons'

export default {
  name: 'MapPage',
  components: {
    PageHeader,
    Button,
    Modal,
    Input,
    Textarea,
    PlusIcon
  },
  setup() {
    const showAddModal = ref(false)
    const newSpace = ref({
      name: '',
      note: ''
    })

    // 使用相对于 public 目录的路径
    const placeholderUrl = '/placeholder-photo.jpg'
    
    const photos = Array.from({ length: 8 }, (_, i) => ({
      url: placeholderUrl,
      note: i === 0 ? '我的秘密基地' : i === 1 ? '工作区一角' : '这是照片备注'
    }))

    const getPolaroidStyle = (index) => {
      // 随机旋转
      const rotation = (Math.random() * 12 - 6).toFixed(1)
      // 随机尺寸
      const scale = (0.85 + Math.random() * 0.15).toFixed(2)
      
      return {
        transform: `rotate(${rotation}deg) scale(${scale})`,
        zIndex: Math.floor(Math.random() * 10)
      }
    }

    const handleAddSpace = () => {
      // 这里暂时只做关闭逻辑
      console.log('添加新空间:', newSpace.value)
      showAddModal.value = false
    }

    return {
      photos,
      getPolaroidStyle,
      showAddModal,
      newSpace,
      handleAddSpace
    }
  }
}
</script>

<style scoped>
.map-page {
  padding: 1.5rem;
  min-height: 100vh;
}

.add-space-btn {
  background: #2c3e50;
  color: white;
  border-radius: 50px;
  padding: 0.6rem 1.5rem;
  transition: all 0.3s ease;
}

.add-space-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.photo-wall-container {
  margin-top: 2rem;
  padding: 1rem;
  perspective: 1000px;
}

/* 白板样式 */
.whiteboard {
  background: #fbfbfb; /* 稍微带点磁性白板的灰白色 */
  border: 12px solid #5d4037; /* 实心木框 */
  border-radius: 4px;
  box-shadow: 
    inset 0 0 40px rgba(0, 0, 0, 0.05),
    0 20px 40px rgba(0, 0, 0, 0.3);
  min-height: 70vh;
  position: relative;
  padding: 3rem;
  background-image: 
    radial-gradient(#e0e0e0 1px, transparent 1px);
  background-size: 40px 40px; /* 隐约的白板纹理 */
}

/* 白板笔装饰 */
.marker {
  position: absolute;
  width: 120px;
  height: 15px;
  border-radius: 8px;
  bottom: -35px;
  right: 60px;
  box-shadow: 2px 5px 5px rgba(0,0,0,0.2);
}
.marker-blue { background: #1976d2; right: 200px; transform: rotate(2deg); }
.marker-red { background: #d32f2f; transform: rotate(-3deg); }

.photo-wall {
  display: flex;
  flex-wrap: wrap;
  gap: 4rem;
  justify-content: center;
  align-items: flex-start;
}

/* 拍立得样式 */
.polaroid-wrapper {
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.polaroid-wrapper:hover {
  transform: rotate(0deg) scale(1.05) translateY(-10px) !important;
  z-index: 100 !important;
}

.polaroid {
  background: #fff;
  padding: 12px 12px 45px 12px;
  box-shadow: 
    0 10px 25px rgba(0, 0, 0, 0.15),
    0 2px 5px rgba(0, 0, 0, 0.1);
  border-radius: 1px;
  display: flex;
  flex-direction: column;
  max-width: 260px;
  position: relative;
}

/* 模拟胶带效果 */
.polaroid::before {
  content: "";
  position: absolute;
  top: -15px;
  left: 50%;
  transform: translateX(-50%) rotate(-2deg);
  width: 80px;
  height: 25px;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(2px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  z-index: 1;
}

.photo-container {
  width: 100%;
  /* 移除固定宽高比，让其适应内容 */
  overflow: hidden;
  background: #f5f5f5;
  border: 1px solid #eee;
}

.photo-container img {
  display: block;
  width: 100%;
  height: auto; /* 保证原始长宽比 */
  object-fit: contain;
  filter: sepia(0.1) contrast(1.1); /* 胶片质感 */
}

.polaroid-caption {
  margin-top: 18px;
  text-align: center;
}

.handwritten {
  font-family: 'Kaiti', 'STKaiti', 'Ma Shan Zheng', cursive;
  font-size: 1.2rem;
  color: #2c3e50;
  display: block;
  padding: 0 5px;
  word-wrap: break-word;
}

/* 弹窗表单样式 */
.add-space-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 1rem 0;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #475569;
  font-size: 0.95rem;
}

.upload-placeholder {
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-placeholder:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.upload-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .whiteboard {
    padding: 1.5rem;
    border-width: 8px;
  }
  .photo-wall {
    gap: 2rem;
  }
  .polaroid {
    max-width: 180px;
  }
}
</style>
