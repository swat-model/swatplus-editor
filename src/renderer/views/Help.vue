<script setup lang="ts">
	import { reactive, onMounted } from 'vue';
	import { useHelpers } from '@/helpers';

	const { api, constants, errors, utilities } = useHelpers();

	let page:any = reactive({
		loading: false,
		error: null
	});

	let apiCheck:any = reactive({
		editor: '',
		pythonVersion: 'N/A'
	});

	async function getHelp() {
		page.loading = true;
		page.error = null;

		try {
			const response = await api.get('/');
			apiCheck.editor = response.data.editor;
			apiCheck.pythonVersion = response.data.pythonVersion;
		} catch (error) {
			page.error = errors.logError(error, 'Unable to connect to SWAT+ API.');
			apiCheck.editor = 'API call unsuccessful';
		}
		
		page.loading = false;
	}

	onMounted(async () => await getHelp());
</script>

<template>
	<v-main class="layout-fix">
		<div class="py-3 px-6">
			<v-row>
				<v-col cols="12" md="6">
					<v-card class="mb-6">
						<v-card-title>Help Using SWAT+ Editor</v-card-title>
						<v-card-text>
							<p class="text-medium-emphasis">
							SWAT+ Editor adalah antarmuka ke SWAT+ yang memungkinkan pengguna untuk mengimpor proyek dari GIS, memodifikasi input SWAT+, menulis file teks, dan menjalankan model.
							</p>
						</v-card-text>
					</v-card>

					<v-card class="mb-6">
						<v-card-title>Troubleshooting</v-card-title>
						<v-card-text>
							<p class="text-medium-emphasis mb-0">
								Silakan kirim informasi di bawah ini ke 
								<open-in-browser url="https://groups.google.com/d/forum/swatplus-editor" text="user group" class="text-primary"></open-in-browser>
								beserta pesan kesalahan Anda.
							</p>
						</v-card-text>
						<v-table density="compact">
							<tbody>
								<tr><th class="min">SWAT+ Editor Version</th><td>{{ constants.appSettings.version }}</td></tr>
								<tr><th class="min">Platform</th><td>{{ constants.globals.platform }}</td></tr>
								<tr><th class="min">Python Mode</th><td>{{ constants.appSettings.python || constants.globals.dev_mode ? 'Yes' : 'Compiled' }}</td></tr>
								<tr><th class="min">Python Version</th><td>{{ apiCheck.pythonVersion }}</td></tr>
								<tr><th class="min">API Check</th><td>{{ apiCheck.editor }}</td></tr>
								<tr><th class="min">API Port</th><td>{{ constants.globals.api_port }}</td></tr>
								<tr><th class="min">Development Mode</th><td>{{ constants.globals.dev_mode ? 'Yes' : 'No' }}</td></tr>
								<tr><th class="min">Locale</th><td>{{ constants.globals.locale }}</td></tr>
							</tbody>
						</v-table>
					</v-card>

					<v-card class="mb-6">
						<v-card-title>Tools Compatibility with SWAT+ Editor {{ constants.appSettings.version }}</v-card-title>
						<v-card-text>
							<p class="text-medium-emphasis mb-0">
								Kami menyadari bahwa kami memiliki banyak alat dengan berbagai versi. Mohon pastikan bahwa saat Anda memperbarui satu alat, alat tersebut tetap kompatibel dengan alat Anda yang lain.
							</p>
						</v-card-text>
						<v-table density="compact">
							<tbody>
								<tr><th class="min">SWAT+ Model</th><td>{{ constants.appSettings.swatplus }} (*see note below)</td></tr>
								<tr><th class="min">QSWAT+</th><td>&gt;= 2.5.3</td></tr>
								<tr><th class="min">SWAT+ Toolbox</th><td>&gt;= 2.0</td></tr>
							</tbody>
						</v-table>
						<v-card-text>
							<p class="text-medium-emphasis mb-0">
								*Note: Meskipun Anda dapat mengubah versi SWAT+ yang digunakan di editor, kami menyarankan untuk melakukannya dengan hati-hati dan dengan pengetahuan tentang perubahan model antar versi.
								Jika ada perubahan file input dan output, Anda mungkin mengalami kesalahan atau hasil yang tidak akurat. Untuk mengubah versi model Anda, buka tab <router-link to="/run">Run</router-link> 
								lalu pilih salah satu versi bawaan dari menu tarik-turun, atau klik ikon roda gigi untuk mendapatkan petunjuk lanjutan.
							</p>
						</v-card-text>
					</v-card>

					<v-card class="mb-6">
						<v-card-title>Seputar SWAT+</v-card-title>
						<v-card-text>
							<p class="text-medium-emphasis mb-0">
								Soil and Water Assessment Tool Plus (SWAT+) adalah model domain publik yang dikembangkan bersama oleh
								USDA Agricultural Research Service (USDA-ARS) dan Texas A&M AgriLife Research, bagian dari Sistem Universitas Texas A&M.
								SWAT+ adalah model skala DAS kecil hingga DAS sungai untuk mensimulasikan kualitas dan kuantitas air permukaan dan air tanah serta memprediksi
								dampak lingkungan dari penggunaan lahan, praktik pengelolaan lahan, dan perubahan iklim. SWAT banyak digunakan dalam menilai pencegahan dan pengendalian erosi tanah,
								pengendalian pencemaran sumber non-titik, dan pengelolaan regional di DAS.
							</p>
						</v-card-text>
					</v-card>

					<v-card class="mb-6">
						<v-card-title>Disclaimer</v-card-title>
						<v-card-text>
							<p class="text-medium-emphasis mb-0">
								Informasi yang terdapat dalam perangkat lunak ini ditawarkan sebagai layanan publik. Merupakan tanggung jawab pengguna untuk memverifikasi keakuratan,
								kelengkapan, ketepatan waktu, kualitas, atau kesesuaian untuk penggunaan tertentu dari informasi/perangkat lunak yang disediakan. Baik Grassland,
								Soil & Water Research Laboratory (GSWRL), Blackland Research Center (BRC), maupun Texas A&M AgriLife Research (TALR) tidak membuat klaim,
								jaminan, atau garansi apa pun tentang keakuratan, kelengkapan, ketepatan waktu, kualitas, atau kesesuaian untuk penggunaan tertentu dari perangkat lunak ini.
								GSWRL, BRC, dan TALR menolak semua tanggung jawab atas klaim atau kerusakan apa pun yang mungkin timbul dari penyediaan situs web atau informasi/
								perangkat lunak yang terdapat di dalamnya. Pengguna perangkat lunak ini menanggung semua tanggung jawab dan melepaskan semua klaim atau tuntutan hukum terhadap
								GSWRL, BRC, dan TALR atas semua penggunaan dan ketergantungan pada informasi/perangkat lunak tersebut. GSWRL, BRC, dan TALR tidak mendukung entitas komersial,
								produk, konsultan, atau dokumentasi apa pun yang mungkin dirujuk dalam perangkat lunak ini. Informasi yang terdapat dalam perangkat lunak ini disediakan
								untuk tujuan informasi umum, dan tidak dimaksudkan sebagai ajakan atau penawaran untuk menjual sehubungan dengan produk atau layanan apa pun.
								Segala referensi kepada entitas komersial, produk, atau konsultan hanya untuk tujuan informasi.
							</p>
						</v-card-text>
					</v-card>
				</v-col>
				<v-col cols="12" md="6">
					<v-card class="mb-6">
						<v-list>
							<v-list-subheader class="text-uppercase">Docs</v-list-subheader>
							<v-list-item @click="utilities.openUrl('https://swatplus.gitbook.io/docs/')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-book</v-icon></template>
								SWAT+ Editor Documentation
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://swatplus.gitbook.io/io-docs/')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-book</v-icon></template>
								SWAT+ Input/Output Documentation
							</v-list-item>
						</v-list>
					</v-card>

					<v-card class="mb-6">
						<v-list>
							<v-list-subheader class="text-uppercase">Sample Data</v-list-subheader>
							<v-list-item @click="utilities.openUrl('https://swatplus.gitbook.io/docs/user/editor/inputs/sample-data')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-database</v-icon></template>
								Example Data Formats for SWAT+ Editor
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://swatplus.gitbook.io/docs/getting-started')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-database</v-icon></template>
								Demo Project for SWAT+ Editor
							</v-list-item>
						</v-list>
					</v-card>

					<v-card class="mb-6">
						<v-list>
							<v-list-subheader class="text-uppercase">User Groups</v-list-subheader>
							<v-list-item @click="utilities.openUrl('https://groups.google.com/d/forum/swatplus')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-users</v-icon></template>
								SWAT+ Model User Group (the model itself)
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://groups.google.com/d/forum/swatplus-editor')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-users</v-icon></template>
								SWAT+ Editor User Group (this interface)
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://groups.google.com/d/forum/qswatplus')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-users</v-icon></template>
								QSWAT+ User Group (GIS interface)
							</v-list-item>
						</v-list>
					</v-card>

					<v-card class="mb-6">
						<v-list>
							<v-list-subheader class="text-uppercase">Additional Resources</v-list-subheader>
							<v-list-item @click="utilities.openUrl('https://swat.tamu.edu/software/plus')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-globe</v-icon></template>
								SWAT+ Website
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://github.com/swat-model/swatplus')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fab fa-github</v-icon></template>
								SWAT+ Github
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://github.com/swat-model/swatplus-editor')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fab fa-github</v-icon></template>
								SWAT+ Editor Github
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://github.com/swat-model/QSWATPlus')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fab fa-github</v-icon></template>
								QSWAT+ Github
							</v-list-item>
							<v-list-item @click="utilities.openUrl('https://plus.swat.tamu.edu')" border="t" class="text-primary">
								<template #prepend><v-icon class="text-medium-emphasis">fas fa-box-archive</v-icon></template>
								SWAT+ Version Archive
							</v-list-item>
						</v-list>
					</v-card>
					
				</v-col>
			</v-row>
		</div>
	</v-main>
</template>

