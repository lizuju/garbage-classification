import { createApp } from 'vue'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap'
import './styles/index.css'
import App from './App.vue'
import router from './router'
import { revealDirective } from './directives/reveal';

const app = createApp(App)

app.directive('reveal', revealDirective);
app.use(router)
app.mount('#app')