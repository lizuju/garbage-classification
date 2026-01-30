// src/directives/reveal.js

export const revealDirective = {
  mounted(el, binding) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          // 元素进入视口，加上 active 类
          el.classList.add('active');
          // 动画只跑一次，跑完就停止观察，节省性能
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.1 });

    // 默认加上基础动画类
    el.classList.add('hero-fade-in');
    
    // 开始观察
    observer.observe(el);
  }
};