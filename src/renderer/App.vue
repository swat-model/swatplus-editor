<script setup lang="ts">
	import { reactive, ref, onMounted } from 'vue'
	const electron = window.electronApi;

	let globals:any = {
		dev_mode: true,
		platform: null,
		project_path: null,
		version: null
	}

	globals = electron.getGlobals();
	electron.setWindowTitle(`SWAT+ Editor v${globals.version}`);
	
	let page:any = reactive({
		errors: false,
		projectPath: globals.project_path,
		colorTheme: 'auto'
	})

	function quitApp():void {
		electron.quitApp();
	}

	function getColorTheme():void {
		let colorTheme = localStorage.getItem('colorTheme');
		setColorTheme(colorTheme);
	}

	function setColorTheme(colorTheme:string|null):void {
		if (colorTheme === null) colorTheme = 'auto';
		page.colorTheme = colorTheme;
		electron.setColorTheme(colorTheme);
		document.documentElement.setAttribute('data-bs-theme', colorTheme);
		localStorage.setItem('colorTheme', colorTheme);
	}

	onMounted(() => getColorTheme());
</script>

<template>
	<div id="app">
		<main class="d-flex flex-nowrap">
			<div class="d-flex flex-column flex-shrink-0 p-3 text-bg-dark" style="width: 280px;">
				<div class="fs-4">SWAT+ Editor</div>
				<hr />
				<ul class="nav nav-pills flex-column mb-auto">
					<li class="nav-item"><a href="#">Test</a></li>
				</ul>
				<hr />
				<div>
					<svg xmlns="http://www.w3.org/2000/svg" class="d-none">
						<symbol id="check2" viewBox="0 0 16 16">
						<path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z"/>
						</symbol>
						<symbol id="circle-half" viewBox="0 0 16 16">
						<path d="M8 15A7 7 0 1 0 8 1v14zm0 1A8 8 0 1 1 8 0a8 8 0 0 1 0 16z"/>
						</symbol>
						<symbol id="moon-stars-fill" viewBox="0 0 16 16">
						<path d="M6 .278a.768.768 0 0 1 .08.858 7.208 7.208 0 0 0-.878 3.46c0 4.021 3.278 7.277 7.318 7.277.527 0 1.04-.055 1.533-.16a.787.787 0 0 1 .81.316.733.733 0 0 1-.031.893A8.349 8.349 0 0 1 8.344 16C3.734 16 0 12.286 0 7.71 0 4.266 2.114 1.312 5.124.06A.752.752 0 0 1 6 .278z"/>
						<path d="M10.794 3.148a.217.217 0 0 1 .412 0l.387 1.162c.173.518.579.924 1.097 1.097l1.162.387a.217.217 0 0 1 0 .412l-1.162.387a1.734 1.734 0 0 0-1.097 1.097l-.387 1.162a.217.217 0 0 1-.412 0l-.387-1.162A1.734 1.734 0 0 0 9.31 6.593l-1.162-.387a.217.217 0 0 1 0-.412l1.162-.387a1.734 1.734 0 0 0 1.097-1.097l.387-1.162zM13.863.099a.145.145 0 0 1 .274 0l.258.774c.115.346.386.617.732.732l.774.258a.145.145 0 0 1 0 .274l-.774.258a1.156 1.156 0 0 0-.732.732l-.258.774a.145.145 0 0 1-.274 0l-.258-.774a1.156 1.156 0 0 0-.732-.732l-.774-.258a.145.145 0 0 1 0-.274l.774-.258c.346-.115.617-.386.732-.732L13.863.1z"/>
						</symbol>
						<symbol id="sun-fill" viewBox="0 0 16 16">
						<path d="M8 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM8 0a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 0zm0 13a.5.5 0 0 1 .5.5v2a.5.5 0 0 1-1 0v-2A.5.5 0 0 1 8 13zm8-5a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2a.5.5 0 0 1 .5.5zM3 8a.5.5 0 0 1-.5.5h-2a.5.5 0 0 1 0-1h2A.5.5 0 0 1 3 8zm10.657-5.657a.5.5 0 0 1 0 .707l-1.414 1.415a.5.5 0 1 1-.707-.708l1.414-1.414a.5.5 0 0 1 .707 0zm-9.193 9.193a.5.5 0 0 1 0 .707L3.05 13.657a.5.5 0 0 1-.707-.707l1.414-1.414a.5.5 0 0 1 .707 0zm9.193 2.121a.5.5 0 0 1-.707 0l-1.414-1.414a.5.5 0 0 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .707zM4.464 4.465a.5.5 0 0 1-.707 0L2.343 3.05a.5.5 0 1 1 .707-.707l1.414 1.414a.5.5 0 0 1 0 .708z"/>
						</symbol>
					</svg>

					<div class="dropdown bd-mode-toggle">
						<button class="btn btn-primary btn-sm dropdown-toggle d-flex align-items-center"
								id="bd-theme"
								type="button"
								aria-expanded="false"
								data-bs-toggle="dropdown"
								aria-label="Toggle theme (auto)">
							<svg class="bi my-1 theme-icon-active" width="1em" height="1em">
								<use v-if="page.colorTheme === 'light'" href="#sun-fill"></use>
								<use v-else-if="page.colorTheme === 'dark'" href="#moon-stars-fill"></use>
								<use v-else href="#circle-half"></use>
							</svg>
							<span class="visually-hidden" id="bd-theme-text">Toggle theme</span>
						</button>
						<ul class="dropdown-menu dropdown-menu-end shadow" aria-labelledby="bd-theme-text">
							<li>
								<button type="button" @click="setColorTheme('light')" class="dropdown-item d-flex align-items-center">
								<svg class="bi me-2 opacity-50 theme-icon" width="1em" height="1em"><use href="#sun-fill"></use></svg>
								Light
								<svg class="bi ms-auto d-none" width="1em" height="1em"><use href="#check2"></use></svg>
								</button>
							</li>
							<li>
								<button type="button" @click="setColorTheme('dark')" class="dropdown-item d-flex align-items-center">
								<svg class="bi me-2 opacity-50 theme-icon" width="1em" height="1em"><use href="#moon-stars-fill"></use></svg>
								Dark
								<svg class="bi ms-auto d-none" width="1em" height="1em"><use href="#check2"></use></svg>
								</button>
							</li>
							<li>
								<button type="button" @click="setColorTheme('auto')" class="dropdown-item d-flex align-items-center">
								<svg class="bi me-2 opacity-50 theme-icon" width="1em" height="1em"><use href="#circle-half"></use></svg>
								Auto
								<svg class="bi ms-auto d-none" width="1em" height="1em"><use href="#check2"></use></svg>
								</button>
							</li>
						</ul>
					</div>
				</div>
			</div>

			<div id="content-window" class="flex-grow-1 d-flex flex-column">
				<div id="inner-content-window" class="py-3 px-4 flex-column flex-grow-1 mb-auto">
					<div>
						<h1 class="h3">Help with SWAT Check</h1>

						<p>
							This version of SWAT Check has been tested with <b>SWAT 2012 revisions up to 688</b>. 
							SWAT 2009 revisions 500 or earlier may not run properly. This version is also NOT compatible with SWAT+.
							For SWAT+, SWAT+ Check is included with <open-in-browser url="https://swat.tamu.edu/software/plus" text="SWAT+ Editor" />.
						</p>

						<ul class="list-group list-group-flush border-top border-bottom">
							<li class="list-group-item"><open-in-browser url="https://swat.tamu.edu/software/swat-check/" text="SWAT Check Website" /></li>
							<li class="list-group-item"><open-in-browser url="https://swat.tamu.edu/" text="SWAT Website" /></li>
							<li class="list-group-item"><open-in-browser url="http://groups.google.com/group/swatuser" text="SWAT User Support Group" /></li>
						</ul>

						<div class="card mt-4">
							<div class="card-header">
								<h4 class="mb-0">Troubleshooting</h4>
							</div>
							<div class="card-body">
								<p>
									Trouble running SWAT Check? Please send the information below to the user group along with your error message.
								</p>
								<div>SWAT Check Version: {{ globals.version }}</div>
								<div>Platform: {{ globals.platform }}</div>
								<div>Project CMD Input: {{ globals.project_path }}</div>
								<div>Development Mode: {{ globals.dev_mode ? 'Yes' : 'No' }}</div>
							</div>
						</div>
					</div>
				</div>
				<div class="border-top p-3 d-flex">
					<button type="button" class="btn btn-secondary" @click="quitApp">Exit</button>
				</div>
			</div>
		</main>
	</div>
</template>

<style lang="scss">
	@import 'app.scss';
</style>
