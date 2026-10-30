# nginx镜像compose/nginx/Dockerfile

FROM nginx:1.25.3

# 删除原有配置文件，创建静态资源文件夹和ssl证书保存文件夹
RUN rm /etc/nginx/conf.d/default.conf \
&& mkdir -p /var/www/static \
&& mkdir -p /var/www/png \
&& mkdir -p /var/www/media \
&& mkdir -p /usr/share/nginx/ssl \
&& mkdir -p /var/www/front_end

# 设置Media文件夹用户和用户组为Linux默认nginx, 并给予可读和可执行权限,
RUN chown -R nginx:nginx /var/www//media \
&& chmod -R 775 /var/www//media \
&& chown -R nginx:nginx /var/www/front_end \
&& chown -R nginx:nginx /var/www/png

# 添加配置文件
ADD ./nginx.conf /etc/nginx/conf.d/

# 关闭守护模式
CMD ["nginx", "-g", "daemon off;"]
