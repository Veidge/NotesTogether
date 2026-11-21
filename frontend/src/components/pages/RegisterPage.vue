<script setup lang="ts">
import {toTypedSchema} from '@vee-validate/zod'
import * as z from 'zod'
import {useForm} from "vee-validate"
import HeaderBase from "../ui/HeaderBase.vue";
import {useAuthStore} from "../../stores/auth";
import {useRouter} from "vue-router";
import { useToastStore } from "../../stores/toast";
import type { ApiError } from "../../services/api";

const formSchema = toTypedSchema(
    z.object({
        displayName: z.string().min(3, "Отображаемое имя должно содержать минимум 3 символа.")
            .max(25, "Отображаемое имя должно содержать максимум 25 символов."),
        username: z.string().min(3, "Имя пользователя должно содержать минимум 3 символа.")
            .max(25, "Имя пользователя должно содержать максимум 25 символов."),
        password: z.string().min(8, "Пароль должен содержать минимум 8 символов."),
        confirmPassword: z.string().min(8, "Пароль должен содержать минимум 8 символов."),
    }).refine((data) => data.password === data.confirmPassword, {
        message: "Пароли не совпадают",
        path: ["confirmPassword"],
    })
)

const form = useForm({
    validationSchema: formSchema,
})

const [displayName, displayNameAttrs] = form.defineField('displayName');
const [username, usernameAttrs] = form.defineField('username');
const [password, passwordAttrs] = form.defineField('password');
const [confirmPassword, confirmPasswordAttrs] = form.defineField('confirmPassword');

const authStore = useAuthStore();
const router = useRouter();
const toastStore = useToastStore();


const onSubmit = form.handleSubmit(async (values) => {
    try {
        await authStore.register({
            displayName: values.displayName,
            username: values.username,
            password: values.password
        });
        toastStore.addToast("success", "Новый пользователь успешно создан");
        await router.push({ name: "login" });
    } catch (error) {
        if (error instanceof Error && "status" in error && typeof error.status === "number") {
            const apiError = error as ApiError;
            toastStore.addToast("error", `Ошибка сервера - HTTP ${apiError.status} - ${apiError.detail}`);
        } else {
            toastStore.addToast("error", error instanceof TypeError
                    ? "Не удалось связаться с сервером. Проверьте подключение."
                    : "Не удалось выполнить регистрацию. Попробуйте ещё раз."
            );
        }
    }
}, () => {
        toastStore.addToast("error", "Заполните все поля регистрации.");
    }
);

</script>

<template>
    <HeaderBase/>
    <div class="w-full h-[87vh] flex items-center justify-center">
        <div class="w-[80%] md:w-[50%] lg:w-[40%] h-screen/2 md:h-screen/2.5 justify-items-center">
            <div class="w-full h-full rounded-[10px] bg-surface py-6 px-3">
                <form @submit="onSubmit">
                    <div class="flex flex-col gap-2">
                        <label for="displayName" class="p-2 mx-1">Отображаемое имя</label>
                        <p class="mx-3 text-red-600"
                           v-if="form.errors.value.displayName && form.errors.value.displayName !== 'Required'">
                            {{ form.errors.value.displayName }}
                        </p>
                        <input id="displayName" class="p-2 mx-1 rounded-md border border-accent/60 outline-none
                        focus:ring-2 focus:ring-accent/30 transition-colors"
                               v-model="displayName" v-bind="displayNameAttrs" type="text" placeholder="Введите отображаемое имя"/>

                        <label for="username" class="p-2 mx-1">Имя пользователя</label>
                        <p class="mx-3 text-red-600"
                           v-if="form.errors.value.username && form.errors.value.username !== 'Required'">
                            {{ form.errors.value.username }}
                        </p>
                        <input id="username" class="p-2 mx-1 rounded-md border border-accent/60 outline-none
                        focus:ring-2 focus:ring-accent/30 transition-colors"
                               v-model="username" v-bind="usernameAttrs" type="text" placeholder="Введите имя пользователя"/>

                        <label for="password" class="p-2 mx-1">Пароль</label>
                        <p class="mx-3 text-red-600"
                           v-if="form.errors.value.password && form.errors.value.password !== 'Required'">
                            {{ form.errors.value.password }}
                        </p>
                        <input id="password" class="p-2 mx-1 rounded-md border border-accent/60 outline-none
                        focus:ring-2 focus:ring-accent/30 transition-colors"
                               v-model="password" v-bind="passwordAttrs" type="password" placeholder="Введите пароль"/>

                        <label for="confirmPassword" class="p-2 mx-1">Подтверждение пароля</label>
                        <p class="mx-3 text-red-600"
                           v-if="form.errors.value.confirmPassword">
                            {{ form.errors.value.confirmPassword }}
                        </p>
                        <input id="confirmPassword" class="p-2 mx-1 rounded-md border border-accent/60 outline-none
                        focus:ring-2 focus:ring-accent/30 transition-colors"
                               v-model="confirmPassword" v-bind="confirmPasswordAttrs" type="password" placeholder="Повторите пароль"/>
                    </div>
                    <div class="flex justify-center mt-6">
                        <button type="submit" class="w-[70%] md:w-[45%] py-2 rounded-md bg-accent hover:bg-accent/80 active:bg-accent/60 cursor-pointer transition-colors">
                            Зарегистрироваться
                        </button>
                    </div>
                </form>
                <div class="flex justify-center mt-3">
                    <p>Уже есть аккаунт? <RouterLink to="/login" class="text-accent">Войдите</RouterLink></p>
                </div>
            </div>
        </div>
    </div>
</template>
