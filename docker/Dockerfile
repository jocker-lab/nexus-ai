FROM python:3.12-slim

ARG USER_UID=1000
ARG USER_GID=1000
ARG USERNAME=sandbox

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 1. 创建用户（root 阶段）
RUN groupadd -g ${USER_GID} ${USERNAME} && \
    useradd -u ${USER_UID} -g ${USERNAME} -m -s /bin/bash ${USERNAME}

# 2. 安装系统依赖（root 阶段）
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-noto-cjk-extra \
    fonts-wqy-zenhei \
    fontconfig \
    libfreetype6-dev libpng-dev libjpeg-dev \
    gcc g++ gfortran build-essential \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# 3. 安装 Python 包（root 阶段）
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        numpy==1.26.4 \
        pandas==2.2.0 \
        matplotlib==3.8.3 \
        seaborn==0.13.2 \
        pillow==10.2.0 \
        ipython

# 4. 创建工作目录（root 阶段）
RUN mkdir -p /workspace && \
    chown -R ${USERNAME}:${USERNAME} /workspace

# 5. 【关键】切换到目标用户
USER ${USERNAME}

# 6. 【用户阶段】创建配置目录
RUN mkdir -p /home/${USERNAME}/.config/matplotlib && \
    mkdir -p /home/${USERNAME}/.cache/matplotlib

# 7. 【用户阶段】写入配置文件
RUN echo "font.sans-serif: Noto Sans CJK SC, Noto Sans CJK JP, WenQuanYi Zen Hei, DejaVu Sans" > /home/${USERNAME}/.config/matplotlib/matplotlibrc && \
    echo "axes.unicode_minus: False" >> /home/${USERNAME}/.config/matplotlib/matplotlibrc && \
    echo "backend: Agg" >> /home/${USERNAME}/.config/matplotlib/matplotlibrc

ENV MPLCONFIGDIR=/home/${USERNAME}/.config/matplotlib \
    MPLBACKEND=Agg

WORKDIR /workspace

CMD ["python"]