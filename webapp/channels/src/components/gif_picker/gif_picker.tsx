// Copyright (c) 2015-present Mattermost, Inc. All Rights Reserved.
// See LICENSE.txt for license information.

import type { SyntheticEvent } from "react";
import React, {
    useCallback,
    useMemo,
    useState,
    useEffect,
    useRef,
} from "react";
import { getCurrentUser } from "mattermost-redux/selectors/entities/users";
import store from 'stores/redux_store';
import "./gif_picker.css"; // CSS 파일 import

import GifPickerItems from "./components/gif_picker_items";
import GifPickerSearch from "./components/gif_picker_search";

const GIF_DEFAULT_WIDTH = 500;
const GIF_MARGIN_ENDS = 12;

// 서버 API 설정
const API_BASE_URL =
    process.env.REACT_APP_GIF_API_URL || "http://chlee.postech.ac.kr:5000";

// 로컬 GIF 데이터 타입 정의
type LocalGif = {
    id: string;
    title: string;
    url: string;
    thumbnailUrl?: string;
    width?: number;
    height?: number;
    tags?: string[];
    fileSize?: number;
    isValid?: boolean;
};

// API 응답 타입
type ApiResponse<T> = {
    success: boolean;
    data?: T;
    error?: string;
    message?: string;
    count?: number;
};

type Props = {
    filter: string;
    onGifClick?: (gif: string) => void;
    handleFilterChange: (filter: string) => void;
    getRootPickerNode: () => HTMLDivElement | null;
    localGifs?: LocalGif[];
    onGifUpload?: (gif: LocalGif) => void;
};

// GIF API 클라이언트 클래스
class GifApiClient {
    private baseUrl: string;
    private userId?: string;

    constructor(baseUrl: string = API_BASE_URL, userId?: any) {
        this.baseUrl = baseUrl;
        this.userId = userId;
    }

    async getGifs(): Promise<ApiResponse<LocalGif[]>> {
        try {
            const url = this.userId
                ? `${this.baseUrl}/gifs?userId=${encodeURIComponent(
                      this.userId
                  )}`
                : `${this.baseUrl}/gifs`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("GIF 목록 조회 실패:", error);
            return {
                success: false,
                error: error instanceof Error ? error.message : "Unknown error",
            };
        }
    }

    async addGifWithFile(
        title: string,
        tags: string[],
        gifFile: File
    ): Promise<ApiResponse<LocalGif>> {
        try {
            const base64Data = await this.fileToBase64(gifFile);

            const gifData = {
                title,
                tags,
                base64_data: base64Data,
                ...(this.userId && { userId: this.userId }), // body에 userId 포함
            };

            const response = await fetch(`${this.baseUrl}/gifs`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(gifData),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error("GIF 업로드 실패:", error);
            return {
                success: false,
                error: error instanceof Error ? error.message : "Unknown error",
            };
        }
    }

    async deleteGif(gifId: string): Promise<ApiResponse<LocalGif>> {
        try {
            const url = this.userId
                ? `${this.baseUrl}/gifs/${gifId}?userId=${encodeURIComponent(
                      this.userId
                  )}`
                : `${this.baseUrl}/gifs/${gifId}`;
            const response = await fetch(url, {
                method: "DELETE",
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("GIF 삭제 실패:", error);
            return {
                success: false,
                error: error instanceof Error ? error.message : "Unknown error",
            };
        }
    }

    async searchGifs(query: string): Promise<ApiResponse<LocalGif[]>> {
        try {
            const params = new URLSearchParams({
                q: query,
                ...(this.userId && { userId: this.userId }),
            });
            const response = await fetch(
                `${this.baseUrl}/gifs/search?${params}`
            );
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error("GIF 검색 실패:", error);
            return {
                success: false,
                error: error instanceof Error ? error.message : "Unknown error",
            };
        }
    }

    private fileToBase64(file: File): Promise<string> {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                const result = reader.result as string;
                const base64 = result.split(",")[1];
                resolve(base64);
            };
            reader.onerror = (error) => reject(error);
        });
    }
}

function getUserIdentifier(store: any): string | null {
    try {
        const currentUser = getCurrentUser(store.getState());
        // username(닉네임)을 사용자 식별자로 사용
        return currentUser?.username || null;
    } catch (error) {
        console.error("사용자 정보 가져오기 실패:", error);
        return null;
    }
}

// 사용 예시
const userId = getUserIdentifier(store);
// const currentUser = getCurrentUser(store.getState());
// const userId = currentUser?.id;
// 싱글톤 API 클라이언트 인스턴스
const gifApiClient = new GifApiClient(API_BASE_URL, userId);

const GifPicker = (props: Props) => {
    const [serverGifs, setServerGifs] = useState<LocalGif[]>([]);
    const [filteredGifs, setFilteredGifs] = useState<LocalGif[]>([]);
    const [loadingGifs, setLoadingGifs] = useState<Set<string>>(new Set());
    const [failedGifs, setFailedGifs] = useState<Set<string>>(new Set());
    const [uploadedGifs, setUploadedGifs] = useState<LocalGif[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const [isLoadingFromServer, setIsLoadingFromServer] = useState(true);
    const [serverError, setServerError] = useState<string | null>(null);

    // 서버에서 GIF 목록 가져오기
    const loadServerGifs = useCallback(async () => {
        setIsLoadingFromServer(true);
        setServerError(null);

        try {
            const response = await gifApiClient.getGifs();
            if (response.success && response.data) {
                setServerGifs(response.data);
            } else {
                setServerError(
                    response.error || "GIF 목록을 불러올 수 없습니다."
                );
                console.error("서버에서 GIF 목록 로드 실패:", response.error);
            }
        } catch (error) {
            setServerError("서버 연결에 실패했습니다.");
            console.error("서버 GIF 로드 중 오류:", error);
        } finally {
            setIsLoadingFromServer(false);
        }
    }, []);

    // 컴포넌트 마운트 시 서버에서 GIF 목록 로드
    useEffect(() => {
        loadServerGifs();

        // localStorage에서 업로드된 GIF 불러오기
        const storedGifs = loadUploadedGifsFromStorage();
        setUploadedGifs(storedGifs);
    }, [loadServerGifs]);

    // 전체 GIF 목록 (서버 GIF + 업로드된 GIF + props로 받은 GIF)
    const allGifs = useMemo(() => {
        const propsGifs = props.localGifs || [];
        return [...serverGifs, ...propsGifs, ...uploadedGifs];
    }, [serverGifs, props.localGifs, uploadedGifs]);

    // 검색 필터링 (서버 검색 vs 로컬 필터링)
    useEffect(() => {
        const filterGifs = async () => {
            if (!props.filter.trim()) {
                // 검색어가 없으면 모든 GIF 표시
                setFilteredGifs(allGifs.filter((gif) => gif.isValid !== false));
            } else {
                // 서버 검색 시도
                try {
                    const searchResponse = await gifApiClient.searchGifs(
                        props.filter
                    );
                    if (searchResponse.success && searchResponse.data) {
                        // 서버 검색 결과와 로컬 업로드 GIF 중 매칭되는 것들 합치기
                        const localMatches = uploadedGifs.filter(
                            (gif) =>
                                gif.title
                                    .toLowerCase()
                                    .includes(props.filter.toLowerCase()) ||
                                gif.tags?.some((tag) =>
                                    tag
                                        .toLowerCase()
                                        .includes(props.filter.toLowerCase())
                                )
                        );

                        const propsMatches = (props.localGifs || []).filter(
                            (gif) =>
                                gif.title
                                    .toLowerCase()
                                    .includes(props.filter.toLowerCase()) ||
                                gif.tags?.some((tag) =>
                                    tag
                                        .toLowerCase()
                                        .includes(props.filter.toLowerCase())
                                )
                        );

                        setFilteredGifs([
                            ...searchResponse.data,
                            ...localMatches,
                            ...propsMatches,
                        ]);
                    } else {
                        // 서버 검색 실패 시 로컬 필터링으로 폴백
                        const filtered = allGifs.filter(
                            (gif) =>
                                (gif.title
                                    .toLowerCase()
                                    .includes(props.filter.toLowerCase()) ||
                                    gif.tags?.some((tag) =>
                                        tag
                                            .toLowerCase()
                                            .includes(
                                                props.filter.toLowerCase()
                                            )
                                    )) &&
                                gif.isValid !== false
                        );
                        setFilteredGifs(filtered);
                    }
                } catch (error) {
                    // 네트워크 오류 시 로컬 필터링
                    console.warn("서버 검색 실패, 로컬 필터링 사용:", error);
                    const filtered = allGifs.filter(
                        (gif) =>
                            (gif.title
                                .toLowerCase()
                                .includes(props.filter.toLowerCase()) ||
                                gif.tags?.some((tag) =>
                                    tag
                                        .toLowerCase()
                                        .includes(props.filter.toLowerCase())
                                )) &&
                            gif.isValid !== false
                    );
                    setFilteredGifs(filtered);
                }
            }
        };

        filterGifs();
    }, [props.filter, allGifs, uploadedGifs]);

    // GIF 파일 업로드 처리 (서버 업로드)
    const handleFileUpload = useCallback(
        async (event: React.ChangeEvent<HTMLInputElement>) => {
            const files = event.target.files;
            if (!files || files.length === 0) return;

            setIsUploading(true);

            try {
                for (const file of Array.from(files)) {
                    // 파일 타입 검사
                    if (!file.type.startsWith("image/gif")) {
                        alert(`${file.name}은 GIF 파일이 아닙니다.`);
                        continue;
                    }

                    // 파일 크기 검사 (10MB 제한)
                    const maxSize = 10 * 1024 * 1024;
                    if (file.size > maxSize) {
                        alert(`${file.name}은 너무 큽니다. (최대 10MB)`);
                        continue;
                    }

                    // 서버에 업로드
                    const title = file.name.replace(/\.[^/.]+$/, ""); // 확장자 제거
                    const tags = ["uploaded", "custom"];

                    const response = await gifApiClient.addGifWithFile(
                        title,
                        tags,
                        file
                    );

                    if (response.success && response.data) {
                        // 서버 업로드 성공 시 서버 GIF 목록에 추가
                        setServerGifs((prev) => [...prev, response.data!]);

                        // 상위 컴포넌트에 알림
                        props.onGifUpload?.(response.data);

                        // alert(`${file.name} 업로드 성공!`);
                    } else {
                        // 서버 업로드 실패 시 로컬 저장으로 폴백
                        console.warn(
                            "서버 업로드 실패, 로컬 저장 사용:",
                            response.error
                        );
                        await handleLocalFileUpload(file);
                    }
                }
            } catch (error) {
                console.error("Error uploading GIF:", error);
                alert("GIF 업로드 중 오류가 발생했습니다.");
            } finally {
                setIsUploading(false);
                event.target.value = "";
            }
        },
        [props.onGifUpload]
    );

    // 로컬 파일 업로드 (서버 업로드 실패 시 폴백)
    const handleLocalFileUpload = async (file: File) => {
        try {
            const base64Data = await convertFileToBase64(file);

            const newGif: LocalGif = {
                id: `local-uploaded-${Date.now()}-${Math.random()
                    .toString(36)
                    .substr(2, 9)}`,
                title: file.name.replace(/\.[^/.]+$/, ""),
                url: base64Data,
                thumbnailUrl: base64Data,
                fileSize: file.size,
                isValid: true,
                tags: ["uploaded", "local"],
            };

            setUploadedGifs((prev) => {
                const updated = [...prev, newGif];
                saveUploadedGifsToStorage(updated);
                return updated;
            });

            props.onGifUpload?.(newGif);
            alert(`${file.name} 로컬 저장 완료 (서버 업로드 실패)`);
        } catch (error) {
            console.error("로컬 파일 업로드 실패:", error);
            alert("파일 처리 중 오류가 발생했습니다.");
        }
    };

    // 파일을 Base64로 변환하는 함수
    const convertFileToBase64 = (file: File): Promise<string> => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => {
                if (typeof reader.result === "string") {
                    resolve(reader.result);
                } else {
                    reject(new Error("파일 읽기에 실패했습니다."));
                }
            };
            reader.onerror = () => reject(reader.error);
            reader.readAsDataURL(file);
        });
    };

    // localStorage에 업로드된 GIF 저장
    const saveUploadedGifsToStorage = (gifs: LocalGif[]) => {
        try {
            const gifsToSave = gifs.slice(-20); // 최신 20개만 저장
            localStorage.setItem("uploadedGifs", JSON.stringify(gifsToSave));
        } catch (error) {
            console.error("localStorage 저장 실패:", error);
        }
    };

    // localStorage에서 업로드된 GIF 불러오기
    const loadUploadedGifsFromStorage = (): LocalGif[] => {
        try {
            const stored = localStorage.getItem("uploadedGifs");
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error("localStorage 읽기 실패:", error);
            return [];
        }
    };

    const handleItemClick = useCallback(
        async (gif: LocalGif, event: SyntheticEvent<HTMLElement, Event>) => {
            if (props.onGifClick) {
                event.preventDefault();

                try {
                    // Base64 데이터인 경우 크기 확인 건너뛰기
                    if (!gif.url.startsWith("data:")) {
                        const response = await fetch(gif.url, {
                            method: "HEAD",
                        });
                        const fileSize = parseInt(
                            response.headers.get("content-length") || "0"
                        );
                        const maxSize = 10 * 1024 * 1024; // 10MB 제한

                        if (fileSize > maxSize) {
                            console.warn(`GIF too large: ${fileSize} bytes`);
                            return;
                        }

                        if (!response.ok) {
                            console.error(`GIF not found: ${gif.url}`);
                            return;
                        }
                    }

                    const imageWithMarkdown = `![${gif.title}](${gif.url})`;
                    props.onGifClick(imageWithMarkdown);
                } catch (error) {
                    console.error("Error loading GIF:", error);
                }
            }
        },
        [props.onGifClick]
    );

    const pickerWidth = useMemo(() => {
        const pickerWidth =
            props.getRootPickerNode?.()?.getBoundingClientRect()?.width ??
            GIF_DEFAULT_WIDTH;
        return pickerWidth - 2 * GIF_MARGIN_ENDS;
    }, [props.getRootPickerNode]);

    // GIF 삭제 (서버 또는 로컬)
    const handleRemoveGif = useCallback(
        async (gifId: string) => {
            try {
                // 서버 GIF인 경우 서버에서 삭제
                const isServerGif = serverGifs.some((gif) => gif.id === gifId);
                if (isServerGif) {
                    const response = await gifApiClient.deleteGif(gifId);
                    if (response.success) {
                        setServerGifs((prev) =>
                            prev.filter((gif) => gif.id !== gifId)
                        );
                        alert("GIF가 서버에서 삭제되었습니다.");
                    } else {
                        alert(response.error || "GIF 삭제에 실패했습니다.");
                    }
                } else {
                    // 로컬 업로드 GIF인 경우 로컬에서만 삭제
                    setUploadedGifs((prev) => {
                        const updated = prev.filter((gif) => gif.id !== gifId);
                        saveUploadedGifsToStorage(updated);
                        return updated;
                    });
                }
            } catch (error) {
                console.error("GIF 삭제 중 오류:", error);
                alert("GIF 삭제 중 오류가 발생했습니다.");
            }
        },
        [serverGifs]
    );

    // 서버 새로고침 기능
    const handleRefreshServer = useCallback(() => {
        loadServerGifs();
    }, [loadServerGifs]);

    return (
        <>
            <GifPickerSearchWithAdd
                value={props.filter}
                onChange={props.handleFilterChange}
                onFileUpload={handleFileUpload}
                isUploading={isUploading}
                isLoadingFromServer={isLoadingFromServer}
                serverError={serverError}
                onRefreshServer={handleRefreshServer}
            />
            {isLoadingFromServer ? (
                <div className="gif-picker-loading">
                    <div className="spinner"></div>
                    <p>서버에서 GIF 목록을 불러오는 중...</p>
                </div>
            ) : (
                <LocalGifPickerItems
                    width={pickerWidth}
                    gifs={filteredGifs}
                    onClick={handleItemClick}
                    onRemoveGif={handleRemoveGif}
                    serverError={serverError}
                />
            )}
        </>
    );
};

// 개선된 GIF 검색 컴포넌트
const GifPickerSearchWithAdd = ({
    value,
    onChange,
    onFileUpload,
    isUploading,
    isLoadingFromServer,
    serverError,
    onRefreshServer,
}: {
    value: string;
    onChange: (filter: string) => void;
    onFileUpload: (event: React.ChangeEvent<HTMLInputElement>) => void;
    isUploading: boolean;
    isLoadingFromServer: boolean;
    serverError: string | null;
    onRefreshServer: () => void;
}) => {
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleAddClick = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className="gif-search-container">
            <div className="gif-search-wrapper">
                <input
                    type="text"
                    className="gif-search-input"
                    placeholder="Search GIFs..."
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                />
                {/* <button
                    type="button"
                    className="gif-refresh-button"
                    onClick={onRefreshServer}
                    disabled={isLoadingFromServer}
                    title="서버에서 GIF 목록 새로고침"
                >
                    {isLoadingFromServer ? "⟳" : "↻"}
                </button> */}
                <button
                    type="button"
                    className="gif-add-button"
                    onClick={handleAddClick}
                    disabled={isUploading}
                    title="Add GIF from your device"
                >
                    {isUploading ? (
                        <div className="add-button-spinner"></div>
                    ) : (
                        <span className="add-icon">+</span>
                    )}
                </button>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/gif"
                    multiple
                    onChange={onFileUpload}
                    style={{ display: "none" }}
                />
            </div>
            {serverError && (
                <div className="server-error-message">
                    ⚠️ 서버 연결 오류: {serverError}
                </div>
            )}
        </div>
    );
};

// 로컬 GIF용 아이템 컴포넌트
const LocalGifPickerItems = ({
    width,
    gifs,
    onClick,
    onRemoveGif,
    serverError,
}: {
    width: number;
    gifs: LocalGif[];
    onClick: (gif: LocalGif, event: SyntheticEvent<HTMLElement, Event>) => void;
    onRemoveGif?: (gifId: string) => void;
    serverError: string | null;
}) => {
    const [loadingImages, setLoadingImages] = useState<Set<string>>(new Set());
    const [failedImages, setFailedImages] = useState<Set<string>>(new Set());

    const handleImageLoad = (gifId: string) => {
        setLoadingImages((prev) => {
            const newSet = new Set(prev);
            newSet.delete(gifId);
            return newSet;
        });
    };

    const handleImageError = (gifId: string) => {
        setFailedImages((prev) => new Set(prev).add(gifId));
        setLoadingImages((prev) => {
            const newSet = new Set(prev);
            newSet.delete(gifId);
            return newSet;
        });
    };

    const handleImageLoadStart = (gifId: string) => {
        setLoadingImages((prev) => new Set(prev).add(gifId));
    };

    const handleRemoveClick = (gifId: string, event: React.MouseEvent) => {
        event.stopPropagation();
        if (onRemoveGif) {
            onRemoveGif(gifId);
        }
    };

    if (gifs.length === 0) {
        return (
            <div className="gif-picker-no-results">
                {serverError ? (
                    <p>서버 연결 오류로 인해 GIF를 불러올 수 없습니다.</p>
                ) : (
                    <p>No GIFs found</p>
                )}
            </div>
        );
    }

    return (
        <div className="gif-picker-items" style={{ width }}>
            <div className="gif-grid gif-grid-4-columns">
                {gifs.map((gif) => (
                    <div
                        key={gif.id}
                        className={`gif-item ${
                            loadingImages.has(gif.id) ? "loading" : ""
                        } ${failedImages.has(gif.id) ? "failed" : ""}`}
                        onClick={(event) => {
                            if (!failedImages.has(gif.id)) {
                                onClick(gif, event);
                            }
                        }}
                        role="button"
                        tabIndex={0}
                        onKeyDown={(event) => {
                            if (
                                (event.key === "Enter" || event.key === " ") &&
                                !failedImages.has(gif.id)
                            ) {
                                onClick(gif, event);
                            }
                        }}
                    >
                        {/* 삭제 가능한 GIF에 삭제 버튼 추가 */}
                        {(gif.id.startsWith("uploaded-") ||
                            gif.id.startsWith("local-uploaded-")) &&
                            onRemoveGif && (
                                <button
                                    className="remove-gif-button"
                                    onClick={(e) =>
                                        handleRemoveClick(gif.id, e)
                                    }
                                    title="GIF 삭제"
                                >
                                    ×
                                </button>
                            )}

                        {loadingImages.has(gif.id) && (
                            <div className="gif-loading">
                                <div className="spinner"></div>
                            </div>
                        )}
                        {failedImages.has(gif.id) ? (
                            <div className="gif-error">
                                <span>❌</span>
                                <p>Failed to load</p>
                            </div>
                        ) : (
                            <>
                                <img
                                    src={gif.thumbnailUrl || gif.url}
                                    alt={gif.title}
                                    loading="lazy"
                                    onLoadStart={() =>
                                        handleImageLoadStart(gif.id)
                                    }
                                    onLoad={() => handleImageLoad(gif.id)}
                                    onError={(e) => {
                                        if (
                                            gif.thumbnailUrl &&
                                            e.currentTarget.src ===
                                                gif.thumbnailUrl
                                        ) {
                                            e.currentTarget.src = gif.url;
                                        } else {
                                            handleImageError(gif.id);
                                        }
                                    }}
                                />
                                <div className="gif-overlay">
                                    <span className="gif-title">
                                        {gif.title}
                                    </span>
                                    {gif.id.startsWith("uploaded-") && (
                                        <span className="gif-badge server-badge">
                                            서버
                                        </span>
                                    )}
                                    {gif.id.startsWith("local-uploaded-") && (
                                        <span className="gif-badge local-badge">
                                            로컬
                                        </span>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default GifPicker;
