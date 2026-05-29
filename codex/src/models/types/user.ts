export interface IBase<T = unknown> {
  /** Format: int64 */
  code?: number;
  msg?: string;
  success?: boolean;
  data?: T;
}

export interface IUserInfoVO {
  /** Format: int64 */
  id?: number;
  name?: string;
  nickname?: string;
  avatar?: string;
  /** Format: int64 */
  use?: number;
  /** Format: int64 */
  gender?: number;
  workId?: string;
  domainId?: string;
  email?: string;
  createTime?: string;
  updateTime?: string;
}

export interface ILoginDataVO {
  userInfo?: IUserInfoVO;
  accessToken?: string;
  /** Format: int64 */
  accessExpire?: number;
  refreshToken?: string;
  /** Format: int64 */
  refreshExpire?: number;
}

export interface ITokenDataVO {
  accessToken?: string;
  /** Format: int64 */
  accessExpire?: number;
  refreshToken?: string;
  /** Format: int64 */
  refreshExpire?: number;
}

export interface IUserRoleInfoVO {
  /** Format: int64 */
  id?: number;
  nickname?: string;
  workId?: string;
  domainId?: string;
  email?: string;
  role?: string;
  projectGroupId?: string;
  projectId?: string;
  iterationId?: string;
  createTime?: string;
  updateTime?: string;
}

/** 用户登录请求参数 */
export interface ILoginReq {
  nickname?: string;
  workId?: string;
  domainId?: string;
  password: string;
}

/** 用户登录响应参数 */
export interface IPostUserLoginResp extends IBase<ILoginDataVO> {}

/** 刷新 token请求参数 */
export interface IRefreshReq {
  refreshToken: string;
}

/** 刷新 token响应参数 */
export interface IPostUserRefreshResp extends IBase<ITokenDataVO> {}

/** 退出登录请求参数 */
export interface ILogoutReq {}

/** 退出登录响应参数 */
export interface IPostUserLogoutResp extends IBase {}

/** 查询用户信息请求参数 */
export interface IQueryUserInfoReq {
  nickname?: string;
  workId?: string;
  domainId?: string;
}

/** 查询用户信息响应参数 */
export interface IPostUserQueryUserInfoResp extends IBase<IUserInfoVO> {}

/** 根据项目查询用户角色列表请求参数 */
export interface IQueryUserRoleListByProjectReq {
  projectId: string;
}

/** 根据项目查询用户角色列表响应参数 */
export interface IPostUserQueryUserRoleListByProjectResp extends IBase<Array<IUserRoleInfoVO>> {}

/** 根据迭代查询用户角色列表请求参数 */
export interface IQueryUserRoleListByIterationReq {
  iterationId: string;
}

/** 根据迭代查询用户角色列表响应参数 */
export interface IPostUserQueryUserRoleListByIterationResp extends IBase<Array<IUserRoleInfoVO>> {}
